import random


class battle_container():
    def __init__(self,max_hp=100,physicalStrength=10,defence=10,speed=10,fireStrength=5,iceStrength=5,earthStrength=5,fireDefence=5,iceDefence=5,earthDefence=5):
        self.max_hp=max_hp
        self.hp=max_hp
        self.physicalStrength = physicalStrength
        self.defence = defence
        self.speed = speed
        self.fireStrength = fireStrength
        self.iceStrength = iceStrength
        self.earthStrength = earthStrength
        self.fireDefence = fireDefence
        self.iceDefence = iceDefence
        self.earthDefence = earthDefence
        

class player_battle_container(battle_container):
    def __init__(self, max_hp=100, max_ep=25, physicalStrength=10, defence=10, speed=50, fireStrength=1, iceStrength=1, eartStrength=1, fireDefence=1, iceDefence=1, earthDefence=1,relics=[],specialRelics=[],items={},energyMoves=[0,0,0,0]):
        super().__init__(max_hp, physicalStrength, defence, speed, fireStrength, iceStrength, eartStrength, fireDefence, iceDefence, earthDefence)
        self.max_ep = max_ep
        self.ep=max_ep
        self.relics=relics
        self.specialRelics = specialRelics
        self.items = items
        self.energyMoves = energyMoves
        self.guarding = 1

    def set_energyMoves(self,move1,move2,move3,move4):
        self.energyMoves[0] = move1
        self.energyMoves[1] = move2
        self.energyMoves[2] = move3
        self.energyMoves[3] = move4

    def add_item(self, item, quantity):
        self.items[item] =  quantity

    
    def guard(self):
        self.guarding = 2

    def cancel_guard(self):
        self.guarding = 1


class enemy_battle_container(battle_container):
    def __init__(self, max_hp=100, physicalStrength=10, defence=10, speed=10, fireStrength=5, iceStrength=5, earthStrength=5, fireDefence=5, iceDefence=5, earthDefence=5,name="NULL",ID="",moves={}):
        super().__init__(max_hp, physicalStrength, defence, speed, fireStrength, iceStrength, earthStrength, fireDefence, iceDefence, earthDefence)
        self.name=name
        self.ID = ID
        self.moves=moves


    def make_move(self,opponent):
        randVal = random.random()
        # print(randVal)
        weightCounter=0
        moveCounter = 0
        while weightCounter < randVal:
            weightCounter += list(self.moves.values())[moveCounter]
            moveCounter+=1
        moveCounter-=1
        # print(list(self.moves.keys())[moveCounter].name)
        move = list(self.moves.keys())[moveCounter]
        # print(move)
        damage = 0
        if move.damageType == "Physical":
            damage = int((self.physicalStrength+move.value)*0.75-opponent.defence)
        elif move.damageType == "Fire":
            damage = int((self.fireStrength*move.value)*0.75-(opponent.defence*opponent.fireDefence))
        elif move.damageType == "Earth":
            damage = int((self.earthStrength*move.value)*0.75-(opponent.defence*opponent.earthDefence))
        elif move.damageType == "Ice":
            damage = int((self.iceStrength*move.value)*0.75-(opponent.defence*opponent.iceDefence))
        elif move.damageType == "Heal":
            self.hp+=move.potency
        else:
            print(move.damageType)

        damage = damage // opponent.guarding

        if damage < 0:
            damage = 0

        opponent.hp -= damage


    #decompose above
    def choose_move(self):
        randVal = random.random()
        # print(randVal)
        weightCounter=0
        moveCounter = 0
        while weightCounter < randVal:
            weightCounter += list(self.moves.values())[moveCounter]
            moveCounter+=1
        moveCounter-=1
        # print(list(self.moves.keys())[moveCounter].name)
        move = list(self.moves.keys())[moveCounter]

        print(self.moves.keys())

        return move

    def use_move(self,opponent,move):
        damage = 0
        if move.damageType == "Physical":
            damage = int((self.physicalStrength+move.value)*0.75-opponent.defence)
        elif move.damageType == "Fire":
            damage = int((self.fireStrength*move.value)*0.75-(opponent.defence*opponent.fireDefence))
        elif move.damageType == "Earth":
            damage = int((self.earthStrength*move.value)*0.75-(opponent.defence*opponent.earthDefence))
        elif move.damageType == "Ice":
            damage = int((self.iceStrength*move.value)*0.75-(opponent.defence*opponent.iceDefence))
        elif move.damageType == "Heal":
            self.hp+=move.potency
        else:
            print(move.damageType)

        damage = damage // opponent.guarding

        if damage < 0:
            damage = 0

        opponent.hp -= damage

    
        


class energy_move():
    def __init__(self,name,physicalValue,fireValue,iceValue,earthValue,healValue,EPcost):
        self.name = name
        self.physicalValue = physicalValue
        self.fireValue = fireValue
        self.earthValue = earthValue
        self.iceValue = iceValue
        self.healValue = healValue
        self.EPcost = EPcost


class item():
    def __init__(self,name,effectType,potency):
        self.name = name
        self.effectType = effectType
        self.potency = potency


class enemy_move():
    def __init__(self,name,damageType,value,animNum=1):
        self.name=name
        self.damageType=damageType
        self.value = value
        self.anim = damageType+str(animNum)+"Enemy"


def load_energy_moves():
    ls = []
    file = open("Data/energyMoves.txt","r")

    moves = file.readlines()#
    file.close()
    for i in moves:
        i = i.split(",")
        ls.append(energy_move(i[0],int(i[1]),int(i[2]),int(i[3]),int(i[4]),int(i[5]),int(i[6])))

    return ls

def load_items():
    ls=[]
    file=open("Data/items.txt","r")

    items_file = file.readlines()
    file.close()
    for i in items_file:
        i = i.split(",")
        ls.append(item(i[0],i[1],int(i[2])))

    return ls

def load_enemy_moves():
    ls=[]
    file=open("Data/enemyMoves.txt","r")

    items_file = file.readlines()
    file.close()
    for i in items_file:
        i = i.split(",")
        ls.append(enemy_move(i[0],i[1],int(i[2]),int(i[3]))) 

    return ls

enemy_moves = load_enemy_moves()

def load_enemy(enemyID):
    file = open(f"Data/Enemies/{enemyID}.txt")
    enemyData = file.readlines()
    # print(enemyData)
    file.close()

    for i in range(len(enemyData)):
        enemyData[i]=enemyData[i].removesuffix("\n")

    tempEnemyContainer = enemy_battle_container(name=enemyData[0],max_hp=int(enemyData[1]),physicalStrength=int(enemyData[2]),defence=int(enemyData[3]),speed=int(enemyData[4]),fireStrength=float(enemyData[5]),\
                                                iceStrength=float(enemyData[6]),earthStrength=float(enemyData[7]),fireDefence=float(enemyData[8]),iceDefence=float(enemyData[9]),earthDefence=float(enemyData[10]),\
                                                    ID=enemyID, moves={})

    for i in range(11,len(enemyData)):
        moveData = enemyData[i].split(",")
        for i in range(len(enemy_moves)):
            if enemy_moves[i].name == moveData[0]:
                moveData[0] = enemy_moves[i]
        tempEnemyContainer.moves[moveData[0]] = float(moveData[1])

    return tempEnemyContainer



