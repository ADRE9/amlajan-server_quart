# custom json data validation
class SchemaValidator(object):
    def __init__(self, response={}):
        self.response = response

    def isTrue(self):
        errorMessages = []

        if "displayName" in self.response:
            try:
                name = self.response.get("displayName")
                if name is None:
                    raise Exception("Error")

            except Exception as e:
                errorMessages.append("Name is required")
        
        elif "phoneNumber" in self.response:
            try:
                phone_num = self.response.get("phoneNumber", None)
                if phone_num is None:
                    raise Exception("Error")
                elif len(phone_num) != 10:
                    errorMessages.append("Enter a number between 1-10")
            except Exception as e:
                errorMessages.append("contact number is required ")


        return errorMessages
