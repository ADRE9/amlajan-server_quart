# Amlajan Server

## URL: https://quart-app.herokuapp.com/
## Endpoints:

[GET]  /getAllProviders
    
    - parameter : None
    - response : returns a list of objects containing all the   
    provider

[GET]  /getProviderById

    -parameter : uid(pass the uid of the provider as a header)
    -response  : returns the user object of the specific uid


[POST] /{<string:role>}/addUserdetails

    -parameter : pass the "role" of the provider along with the request

    IF "role"=="provider" , then 
    -request : {
        "uid":"",
        "displayName":"",
        "phoneNumber":"",
        "email":"",
        "location":"",
        "incentive":"",
    }

    if "role"=="patient",then 

    -request : {
        "name":"",
        "uid":""
    }


    -response :  returns the newly created user object

[GET] /checkUserExists
    
    -parameter :  uid(pass the uid of the provider as a header)
    -response : if exists returns the user object otherwise redirect to the "ROLE" page



[POST] /getNearbyProviders

    -parameter : pass the latitude and longitude of the patient
    
    -request : {
        "latitude":  ,
        "longitude":    
    }

    -response : returns a list of objects




[PATCH] /updateProfile

    -parameter : uid(pass the uid of the provider as a header)

    -request : {
        "displayName":"",
        "phoneNumber":"",
        "email":"",
        "location":"",
        "rating": ,
        "role": "",
        "incentive":""
    }

    -response : returns the updated user object



[DELETE] /deleteProvider
    
    -parameter : uid(pass the uid of the provider as a header)
    -response :  "User deleted successfully",200


