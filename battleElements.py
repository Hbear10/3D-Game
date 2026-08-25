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

    #prints out all the attributes of the object
    #useful for testing
    def output_stats(self):
        print(vars(self))
        

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
    def __init__(self,name,physicalValue,fireValue,iceValue,earthValue,healValue,EPcost,animID):
        self.name = name
        self.physicalValue = physicalValue
        self.fireValue = fireValue
        self.earthValue = earthValue
        self.iceValue = iceValue
        self.healValue = healValue
        self.EPcost = EPcost
        self.animID = animID


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


class relic():
    def __init__(self,name:str, description:str, effectDescription:str,image,stat:str,addVal=0,multVal=1):
        self.name = name
        self.description = description
        self.effectDescription = effectDescription
        self.image=image
        self.stat = stat
        self.addVal = addVal
        self.multVal = multVal

def load_relics():
    relicTempList = []
    relicTempList.append(relic("Spikey Band","This will make your attacks hurt more","(Increases Physical Strength by 10%)","SpikeyBand","physicalStrength",multVal=1.1))
    relicTempList.append(relic("Heavy Plating","This plating will dull your opponents blows","(Increases Defence by 10%)","HeavyPlating","defence",multVal=1.1))
    relicTempList.append(relic("Speed Syringe","This special serum will make you move quicker","(Increases speed by 10%)","SpeedSyringe","speed",multVal=1.1))
    relicTempList.append(relic("Fire Shard","This will imporve your ability to use fire","(Increases fire affinity by 10%)","FireShard","fireAffinity",multVal=1.1))
    relicTempList.append(relic("Ice Shard","This will imporve your ability to use ice","(Increases ice affinity by 10%)","IceShard","iceAffinity",multVal=1.1))
    relicTempList.append(relic("Earth Shard","This will imporve your ability to use earth","(Increases earth affinity by 10%)","EarthShard","EarthAffinity",multVal=1.1))
    relicTempList.append(relic("HP","This will increase your HP","(+10 HP)","HPUP","HP",addVal=10))
    relicTempList.append(relic("Battery","This will increase your energy capacity","(+5 EP)","Battery","EP",addVal=5))

    return relicTempList


def relic_apply_stat_change(playerObject: battle_container,relicObject: relic):
    stat = relicObject.stat
    if stat == "physicalStrength":
        playerObject.physicalStrength = (playerObject.physicalStrength + relicObject.addVal) * relicObject.multVal
    elif stat == "defence":
        playerObject.defence = (playerObject.defence + relicObject.addVal) * relicObject.multVal
    elif stat == "speed":
        playerObject.speed = (playerObject.speed + relicObject.addVal) * relicObject.multVal
    elif stat == "fireAffinity":
        playerObject.fireStrength = (playerObject.fireStrength + relicObject.addVal) * relicObject.multVal
        playerObject.fireDefence = (playerObject.fireDefence + relicObject.addVal) * relicObject.multVal
    elif stat == "iceAffinity":
        playerObject.iceStrength = (playerObject.iceStrength + relicObject.addVal) * relicObject.multVal
        playerObject.iceDefence = (playerObject.iceDefence + relicObject.addVal) * relicObject.multVal
    elif stat == "earthAffinity":
        playerObject.earthStrength = (playerObject.earthStrength + relicObject.addVal) * relicObject.multVal
        playerObject.earthDefence = (playerObject.earthDefence + relicObject.addVal) * relicObject.multVal
    elif stat == "HP":
        playerObject.max_hp = (playerObject.max_hp + relicObject.addVal) * relicObject.multVal
        playerObject.hp = (playerObject.hp + relicObject.addVal) * relicObject.multVal
    elif stat == "EP":
        playerObject.max_ep = (playerObject.max_ep + relicObject.addVal) * relicObject.multVal
        playerObject.ep = (playerObject.ep + relicObject.addVal) * relicObject.multVal

    playerObject.output_stats()
    


def load_energy_moves():
    ls = []
    file = open("Data/energyMoves.txt","r")

    moves = file.readlines()#
    file.close()
    for i in moves:
        i = i[:-1]#remove\n
        i = i.split(",")#break into a list
        ls.append(energy_move(i[0],int(i[1]),int(i[2]),int(i[3]),int(i[4]),int(i[5]),int(i[6]),i[7]))

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



