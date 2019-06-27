import json
import sys
import pickle


print("Number of CMD-line arguments: {}".format(len(sys.argv)-1))

if (((len(sys.argv)-1) % 3)!=0):
    print("Wrong number of arguments! It should be 3*N")
    exit()

N = int((len(sys.argv)-1)/3)


data = {}
data["center"] = []
data["spec"] = []

for x in range(N):
    print("Center: {}\n".format(x)+9*"=")
    print("SPEC  : {}\nMOLDEN: {}\n1stExc: {}".format(sys.argv[3*x+1],sys.argv[3*x+2],sys.argv[3*x+3]))
    X = pickle.load(open(sys.argv[3*x+1] ,"rb"))
    shift=(float(sys.argv[3*x+3])-float(X["En"][0])*27.211385)
    print("SHIFT : {}\n".format(shift))
    data["center"].append({"spectrum" :sys.argv[3*x+1],
                           "molden":sys.argv[3*x+2],
                           "excitation":sys.argv[3*x+3],
                           "shift" : shift})


Orbs = []

for center in data["center"]:
    X = pickle.load(open(center["spectrum"],"rb"))
    Molden = open(center["molden"]).readlines()
    idx = [c for c,x in enumerate(Molden) if "[MO]" in x][0]
    header = Molden[:idx]
    header.append("[MO]\n")
    moPart = Molden[idx+1:]
    idx = [c for c,x in enumerate(moPart) if "Sym" in x]

    for i in range(1,len(idx)):
        X = "".join((moPart[idx[i-1]:idx[i]]))
        if "Beta" in X:
            X2 = X.split("\n")
            occ = float([x.split("=")[1] for x in X2 if "Occup=" in x][0])

            if ((occ>0.0) and (occ<1.0)):
                coreEn = float([x.split("=")[1] for x in X2 if "Ene=" in x][0])
                Orbs.append(X)
    
            if (occ==0.0):
                En = float([x.split("=")[1] for x in X2 if "Ene=" in x][0])
                for c,j in enumerate(X2):
                    if "Ene=" in j:
                        X2[c]=" Ene="+str((En-coreEn)*27.211385+float(center["shift"]))
    
                Orbs.append("\n".join(X2))

    X = "".join((moPart[idx[i]:]))
    if "Beta" in X:
        X2 = X.split("\n")
        occ = float([x.split("=")[1] for x in X2 if "Occup=" in x][0])
        if (occ ==0.0):
            En = float([x.split("=")[1] for x in X2 if "Ene=" in x][0])
            for c,j in enumerate(X2):
                if "Ene=" in j:
                    X2[c]=" Ene= "+str((En-coreEn)*27.211385)
            Orbs.append("\n".join(X2))
    center["CoreEnergy"] = coreEn


data["center"] = sorted(data["center"], key=lambda x: x['CoreEnergy'])
for c,i in enumerate(data["center"]):
    i["ID"] = c
    

f = open("spec.molden","w")
f.write("".join(header))
for i in Orbs:
    f.write(i)
f.close()


for spectra in data["center"]:
    X = pickle.load(open(spectra["spectrum"],"rb"))
    for E,X,Y,Z in zip(X["En"],X["Dx"],X["Dy"],X["Dz"]):
        data["spec"].append({"ID" : spectra["ID"],
                             "shift" : float(spectra["shift"]),
                             "En" : float(E*27.211385),
                             "Dx" : float(X),
                             "Dy" : float(Y),
                             "Dz" : float(Z),
                             "Tot": float(X**2+Y**2+Z**2)})


data["spec"] = sorted(data["spec"], key=lambda x: x['En'])

with open("spec.json","w") as outfile:
    json.dump(data,outfile,indent=4)

