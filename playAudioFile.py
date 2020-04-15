import os
import random
#from PIL import Image

list = []

for file in os.listdir("./mp3s"):
    if file.endswith(".mp3"):
        #print(os.path.join("mp3s", file))
        list.append(os.path.join("mp3s",file))


print("List of mp3s: ", list)
print("Number of mp3s: ", len(list))

#Get a random index (range is inclusive)
randomIndex = random.randint(0,len(list)-1)
print("Random index: ", randomIndex)

print("Candidate mp3: ", list[randomIndex])

#Text description of the mp3
print("\n###### DESCRIPTION ######")
fileName = list[randomIndex]
#print("file identifier: ", fileName[0:-4])
fileName = fileName[0:-4] + ".txt"
print("Txt file: ", fileName)

#Image
#im = Image.open(r"imgs/baldEagle.jpg")
#im.show()

f = open(fileName, 'r')
fc = f.read()
print(fc)
f.close

print("\n###### ROUTING TO AUDIO ######")
osCmd = "mpg321 --gain 100 --verbose " + list[randomIndex] #+ " &"
print(osCmd)

#os.system('mpg321 mp3s/frogs.mp3 &')
os.system(osCmd)

