#custom json data validation
class SchemaValidator(object):
    def __init__(self, response={}):
        self.response =response
 
    def isTrue(self):
        errorMessages = []
        try:
            phone_num =  self.response.get("contact_number", None)
            if phone_num is None :
                raise Exception("Error")
            elif len(phone_num)!=10:
                errorMessages.append("Enter a number between 1-10")
        except Exception as e:
            errorMessages.append("contact number is required ")

        try:
            address =  self.response.get("address", None)
            if address is None:
                raise  Exception("Error")
            elif type(address)!=str:
                errorMessages.append("Enter a valid address")
        except Exception as e:
            errorMessages.append("Address  is required!!")

        try:
            latitude =  self.response.get("lat")
            longitude =  self.response.get("long")
            if latitude is None or longitude is None:
                raise  Exception("Error")
            elif type(latitude)!=float or type(longitude)!=float:
                errorMessages.append("Enter a valid cordinate")
        except Exception as e:
            errorMessages.append("Coordinates are required!! ")
        return errorMessages



