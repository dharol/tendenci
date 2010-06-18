from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from base.http import Http403
from invoices.models import Invoice

def view(request, id, guid=None, template_name="invoices/view.html"):
    #if not id: return HttpResponseRedirect(reverse('invoice.search'))
    invoice = get_object_or_404(Invoice, pk=id)

    if not invoice.allow_view_by(request.user, guid): return Http403
    
    #invoice_display = invoice_html_display(request, invoice)
    
    return render_to_response(template_name, {'invoice': invoice}, 
        context_instance=RequestContext(request))
