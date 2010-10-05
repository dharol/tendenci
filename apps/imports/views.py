import os
import time
import cPickle
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.core.urlresolvers import reverse
from django.conf import settings
from perms.utils import is_admin
from base.http import Http403
from imports.forms import UserImportForm
from imports.utils import extract_from_excel, render_excel, handle_uploaded_file, get_user_import_settings, user_import_process
from event_logs.models import EventLog
from user_groups.models import Group, GroupMembership


IMPORT_DIR = os.path.join(settings.MEDIA_ROOT, 'imports')


@login_required
def user_upload_add(request, form_class=UserImportForm, template_name="imports/users.html"):
    if not is_admin(request.user):raise Http403   # admin only page
    
    if request.method == 'POST':
        form = form_class(request.POST, request.FILES)
        if form.is_valid():
            # save the uploaded file
            file_dir = IMPORT_DIR
            
            if not os.path.isdir(file_dir):
                os.makedirs(file_dir)
            f = request.FILES['file']
            file_name = f.name.replace('&', '')
            file_path = os.path.join(file_dir, file_name)
            handle_uploaded_file(f, file_path)
            
            interactive = form.cleaned_data['interactive']
            override = form.cleaned_data['override']
            key = form.cleaned_data['key']
            group = form.cleaned_data['group']
            clear_group_membership = form.cleaned_data['clear_group_membership']
            
            # read the spreadsheet into a dictionary
            data_dict_list = extract_from_excel(file_path)
            
            # generate a unique id for this import
            id = str(int(time.time()))
            
            # store the infor in the session to pass to the next page
            request.session[id] = {'file_name': file_name,
                                   'interactive':interactive, 
                                   'override': override,
                                   'key': key,
                                   'group': group,
                                   'clear_group_membership': clear_group_membership,
                                   'total': len(data_dict_list),
                                   'data_dict_list': data_dict_list}
            
            
            return HttpResponseRedirect(reverse('imports.views.user_upload_preview', args=[id]))
    else:
        form = form_class()
    return render_to_response(template_name, {'form':form}, 
        context_instance=RequestContext(request))
    
@login_required
def user_upload_preview(request, id, template_name="imports/users_preview.html"):
    if not is_admin(request.user):raise Http403   # admin only page
    
    id = str(id)
        
    import_dict = get_user_import_settings(request, id)
    import_dict['file_dir'] = IMPORT_DIR
    
    if not os.path.isfile(os.path.join(import_dict['file_dir'], import_dict['file_name'])):
        return HttpResponseRedirect(reverse('imports.views.user_upload_add'))

    users_list, invalid_list = user_import_process(request, import_dict, preview=True, id=id)
    import_dict['users_list'] = users_list
    import_dict['id'] = id
    import_dict['total'] =  request.session[id].get('total',  0)
    
    #d = request.session[id]
    #d.update({'total': import_dict['total'] - import_dict['count_invalid']})
    #request.session[id] = d
    #d = None
    
    return render_to_response(template_name, import_dict, 
        context_instance=RequestContext(request))
    
    
@login_required
def user_upload_process(request, id, template_name="imports/users_process.html"):
    if not is_admin(request.user):raise Http403   # admin only page

    id = str(id)
    import_dict = get_user_import_settings(request, id)
    if not import_dict:
        return HttpResponseRedirect(reverse('imports.views.user_upload_add'))
    
    import_dict['file_dir'] = IMPORT_DIR
    import_dict['id'] = id
    
    if not os.path.isfile(os.path.join(import_dict['file_dir'], import_dict['file_name'])):
        return HttpResponseRedirect(reverse('imports.views.user_upload_add'))
    
    #reset group - delete all members in the group
    if import_dict['clear_group_membership'] and import_dict['group']:
        GroupMembership.objects.filter(group=import_dict['group']).delete()
    
    #import_dict['next_starting_point'] = 0

    d = request.session[id]
    d.update({'is_completed': False,
              'count_insert': 0,
              'count_update': 0,
              'total_done':0})
    request.session[id] = d
    d = None
    
    
    return render_to_response(template_name, import_dict, 
        context_instance=RequestContext(request))
    
@login_required
def user_upload_subprocess(request, id, template_name="imports/users_subprocess.html"):
    if not is_admin(request.user):raise Http403   # admin only page
    
    id = str(id)
    import_dict = get_user_import_settings(request, id)
    if not import_dict:
        return HttpResponse('')
    
    import_dict['file_dir'] = IMPORT_DIR
    
    if not os.path.isfile(os.path.join(import_dict['file_dir'], import_dict['file_name'])):
        return HttpResponse('')

    
    users_list, invalid_list = user_import_process(request, import_dict, preview=False, id=id)
    import_dict['users_list'] = users_list
    
    # recalculate the total
    import_dict['total_done'] = request.session[id]['total_done']
    import_dict['total_done'] += import_dict['count_insert'] + import_dict['count_update']
    request.session[id]['total_done'] = import_dict['total_done']
    
    d = request.session[id]
    d.update({'total_done': import_dict['total_done']})
    request.session[id] = d
    d = None
    
    import_dict['is_completed'] = request.session[id]['is_completed']
    
    # store the recap - so we can retrieve it later
    recap_file_name = '%s_recap.txt' % id
    recap_path = os.path.join(import_dict['file_dir'], recap_file_name)
    
    if os.path.isfile(recap_path):
        fd = open(recap_path, 'r')
        content = fd.read()
        fd.close()
        recap_dict = cPickle.loads(content)
        recap_dict.update({'users_list':recap_dict['users_list']+import_dict['users_list'],
                           'invalid_list':recap_dict['invalid_list']+invalid_list,
                           'total':import_dict['total'],
                           'total_done':import_dict['total_done'],
                           'count_insert':recap_dict['count_insert']+import_dict['count_insert'],
                           'count_update':recap_dict['count_update']+import_dict['count_update'],
                           'count_invalid':recap_dict['count_invalid']+import_dict['count_invalid']
                           })
        import_dict['count_invalid'] = recap_dict['count_invalid']
    else:
        recap_dict = {'users_list':import_dict['users_list'],
                       'invalid_list':invalid_list,
                       'total':import_dict['total'],
                       'total_done':import_dict['total_done'],
                       'count_insert':import_dict['count_insert'],
                       'count_update':import_dict['count_update'],
                       'count_invalid':import_dict['count_invalid'],
                       'file_name':import_dict['file_name']}
    
    
    fd = open(recap_path, 'w')
    cPickle.dump(recap_dict, fd)
    fd.close()
    # clear the recap_dict
    recap_dict = None
    
    
    if import_dict['is_completed']:
        # log an event
        log_defaults = {
            'event_id' : 129005,
            'event_data': 'User import: %s<br>INSERTS:%d<br>UPDATES:%d<br>INVALID:%d<br>TOTAL:%d' % (import_dict['file_name'], 
                                                                                       import_dict['count_insert'],
                                                                                       import_dict['count_update'], 
                                                                                       import_dict['count_invalid'],
                                                                                       import_dict['total']),
            'description': 'user import',
            'user': request.user,
            'request': request,
        }
        EventLog.objects.log(**log_defaults)
        
        # clear up the session
        del request.session[id]
        
        # remove the imported file
        os.remove(os.path.join(import_dict['file_dir'], import_dict['file_name']))
    
    import_dict['id'] = id
    return render_to_response(template_name, import_dict, 
        context_instance=RequestContext(request))
 
@login_required   
def user_upload_recap(request, id):
    if not is_admin(request.user):raise Http403   # admin only page
    
    recap_file_name = '%s_recap.txt' % str(id)
    recap_path = os.path.join(IMPORT_DIR, recap_file_name)
    
    if os.path.isfile(recap_path):
        import StringIO
        from django.template.defaultfilters import slugify
        from xlwt import Workbook, XFStyle
        
        # restore the recap_dict
        fd = open(recap_path, 'r')
        content = fd.read()
        fd.close()
        
        recap_dict = cPickle.loads(content)
        
        output = StringIO.StringIO()
        export_wb = Workbook()
        sheet1 = export_wb.add_sheet('Recap')
        # title
        sheet1.write(0, 0, 'action')
        sheet1.write(0, 1, 'original row#')
        sheet1.write(0, 2, 'username')
        sheet1.write(0, 3, 'frist_name')
        sheet1.write(0, 4, 'last_name')
        sheet1.write(0, 5, 'email')
        
        # data
        row_idx = 1
        for item_dict in recap_dict['users_list']:
            sheet1.write(row_idx, 0, '%s' % item_dict['ACTION'])
            sheet1.write(row_idx, 1, str(item_dict['ROW_NUM']))
            sheet1.write(row_idx, 2, item_dict['user'].username)
            sheet1.write(row_idx, 3, item_dict['user'].first_name)
            sheet1.write(row_idx, 4, item_dict['user'].last_name)
            sheet1.write(row_idx, 5, item_dict['user'].email)
            
            row_idx += 1
        
        # create another sheet for invalid list    
        if recap_dict['invalid_list']:
            sheet2 = export_wb.add_sheet('Invalid records')
            # title
            sheet2.write(0, 0, 'invalid?')
            sheet2.write(0, 1, 'original row#')
            sheet2.write(0, 2, 'reason')
            
        row_idx = 1
        for invalid_dict in recap_dict['invalid_list']:
            sheet2.write(row_idx, 0, 'invalid')
            sheet2.write(row_idx, 1, invalid_dict['ROW_NUM'])
            sheet2.write(row_idx, 2, invalid_dict['ERROR'])
            row_idx += 1
            
        export_wb.save(output)
        output.seek(0)
        str_out = output.getvalue()
        response = HttpResponse(str_out)
        response['Content-Type'] = 'application/vnd.ms-excel'
        if recap_dict['file_name'] and len(recap_dict['file_name'])>5:
            recap_name = '%s_recap.xls' % slugify((recap_dict['file_name'])[:-4])
        else:
            recap_name = "user_import_recap.xls"
        response['Content-Disposition'] = 'attachment; filename=%s' % (recap_name)
        
        recap_dict = None
        return response
    else:
        raise Http404 
   
@login_required
def download_user_upload_template(request, file_ext='.xls'):
    if not is_admin(request.user):raise Http403   # admin only page
    
    if file_ext == '.csv':
        filename = "import-users.csv"
    else:
        filename = "import-users.xls"
    import_field_list = ['salutation', 'first_name', 'last_name', 'initials', 'display_name',
                         'email', 'email2', 'address', 'address2', 'city', 'state', 'zipcode', 'country', 
                         'company', 'position_title', 'department', 'phone', 'phone2', 'home_phone', 
                         'work_phone', 'mobile_phone', 'fax', 'url', 'dob', 'spouse', 'department',
                         'direct_mail', 'notes', 'admin_notes', 
                         'username', 'password', 'member_number']
    data_row_list = []
    
    return render_excel(filename, import_field_list, data_row_list, file_ext)