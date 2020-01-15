
def fdd_out_dict(success, code, result = None, msg = None, details=None):
    out_dict, error = {}, {}
    out_dict['success'], error['code']= success, code

    if code == 0:
        out_dict["error"]=error
        out_dict["result"] = result
    if code == -1:
        error['message'] = 'no response by: '+ ','.join(details)
        out_dict["error"] = error
        out_dict["result"] = result
    if code == -2:
        error['message'] = "no data available for the FDD application. Not enough"
        out_dict["error"] = error
    if code == -3:
        error["message"] = "no data available for all devices"
        out_dict["error"] = error

    if code == -4:
        error["message"]=msg
        out_dict["error"] = error
        out_dict['success'] = success

    if code == -5:
        error['message'] = msg
        out_dict["error"] = error
        out_dict['success'] = success

    return out_dict

def psd_out_dict(success, code, result = None, msg=None):
    out_dict, error = {}, {}
    out_dict['success'], error['code']= success, code

    if code == 0:
        out_dict["error"]=error
        out_dict["result"] = result
    if code == -1:
        error['message'] = msg

        out_dict["error"] = error

    if code == -4:
        error["message"]=msg
        out_dict["error"] = error
        out_dict['success'] = success

    if code == -5:
        error['message'] = msg
        out_dict["error"] = error
        out_dict['success'] = success
    return out_dict

def integrate_out_dict2(success, code, result = None, msg = None):
    out_dict, error = {}, {}
    out_dict['success'], error['code']= success, code

    if code == 0:
        out_dict["error"]=error
        out_dict["result"] = result
    if code == -1:
        error['message'] = msg

        out_dict["error"] = error

    if code == -4:
        out_dict["error"] = error
        out_dict['success'] = success
        error['message'] = msg
    if code == -5:
        error['message'] = msg
        out_dict["error"] = error
        out_dict['success'] = success
    return out_dict

def integrate_out_dict1(success, code, result = None, msg = None):
    out_dict, error = {}, {}
    out_dict['success'], error['code']= success, code

    if code == 0:
        out_dict["error"]=error
        out_dict["result"] = result
    if code == -1:
        error['message'] = msg

        out_dict["error"] = error

    if code == -4:
        out_dict["error"] = error
        out_dict['success'] = success
        error['message'] = msg
    if code == -5:
        error['message'] = msg
        out_dict["error"] = error
        out_dict['success'] = success
    return out_dict
