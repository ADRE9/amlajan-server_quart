# custom json data validation
class SchemaValidator(object):
    def __init__(self, response={}):
        self.response = response

    def isTrue(self):
        errorMessages = []

        try:
            name = self.response.get("displayName")
            if name is None:
                raise Exception("Error")

        except Exception as e:
            errorMessages.append("Name is required")

        try:
            phone_num = self.response.get("phoneNumber", None)
            if phone_num is None:
                raise Exception("Error")
            elif len(phone_num) != 10:
                errorMessages.append("Enter a number between 1-10")
        except Exception as e:
            errorMessages.append("contact number is required ")

        try:
            latitude = self.response.get("location", None).get("latitude")
            longitude = self.response.get("location", None).get("longitude")
            if latitude is None or longitude is None:
                raise Exception("Error")
            elif type(latitude) != float or type(longitude) != float:
                errorMessages.append("Enter a valid cordinate")
        except Exception as e:
            errorMessages.append({"location": "New Delhi", "latitude": 28.644800, "longitude": 77.216721})
        return errorMessages
