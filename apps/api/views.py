from django.http import HttpResponse
from django.utils import simplejson
from django.views.decorators.csrf import csrf_exempt
from api.utils import validate_api_request


@csrf_exempt  
def api_rp(request):
    """A Recurring Payment api.
       Supported functions: api_add_rp,
                            api_get_rp_token
                            
    Result code: 
        1001 - successful
        E004 - invalid request
        E005 - system error
        
    Test command:
    curl --dump-header - -H "Content-Type: application/json" -X POST 
    --data '{"api_method": "api_add_rp", "email": "jqian@schipul.com", 
    "description": "self signup", "payment_amount": "20",
    "access_id":"jennytest", "time_stamp":"1317505435.040309", 
    "h_sequence":"3b0b9655af8698d3d1b87ea913da3a41"}' 
    http://127.0.0.1:8000/api/rp/
    
    curl --dump-header - -H "Content-Type: application/json" -X POST 
    --data '{"api_method": "api_get_rp_token", "rp_id": "4", 
    "access_id":"jennytest", "time_stamp":"1317505435.040309", 
    "h_sequence":"3b0b9655af8698d3d1b87ea913da3a41"}' 
    http://127.0.0.1:8000/api/rp/
    """
    result_code_success = {'result_code': '1001'}
    result_code_invalid = {'result_code': 'E004'}
    result_code_error = {'result_code': 'E005'}
    
    try:
        data = simplejson.loads(request.raw_post_data)
    except simplejson.JSONDecodeError:
        data = ''
        
    if not isinstance(data, dict):
        return  HttpResponse('')
    
    # SECURITY CHECK - access_id, secret_key(not passed), h_sequence
    is_valid = validate_api_request(data)
    if not is_valid:
        return HttpResponse('')
    
    method = data.get('api_method', '')
    if method == 'api_add_rp':
        from recurring_payments.utils import api_add_rp
        success, ret_data = api_add_rp(data)
    elif method == 'api_get_rp_token':
        from recurring_payments.utils import api_get_rp_token
        success, ret_data = api_get_rp_token(data)
    elif method == 'api_verify_rp_payment_profile':
        from recurring_payments.utils import api_verify_rp_payment_profile
        success, ret_data = api_verify_rp_payment_profile(data)
    else:
        return  HttpResponse('')
        
    if success:
        ret_data.update(result_code_success)
    else:
        ret_data.update(result_code_invalid)
        
    return HttpResponse(simplejson.dumps(ret_data), mimetype='application/json')
    