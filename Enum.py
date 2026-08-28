#Create an Enum class (Enumerator data type used in some programming languages)
#   An enum is a data type where it can only store set values. This makes it more secure 
#   and less error prone than checking values on variables.
#Python doesn't have a built in enum so I made it myself

#Create the Enum Class in this file
#Also create the different enums in this file to be imported

class Enum():
    def __init__(self):
        self.values = []
        self.value  = None
        
    def set_value(self, setter_value):
        if setter_value in self.values:
            self.value = setter_value
        else:
            raise Exception("Error invalid value")
            
            
class StateOfGame(Enum):
    def __init__(self, value=None):
        self.values = ["Moving","Glide","Battle","Battle-Energy","Battle-Item","Battle-Won","MoveUp","PopUp"]
        if value in self.values:
            self.value = value


if __name__ == "__main__":    
    State = StateOfGame()
    State.set_value("Moving")
    print(State.value)
