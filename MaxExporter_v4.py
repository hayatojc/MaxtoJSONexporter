import MaxPlus
from collections import OrderedDict
import json
import os

#MaxPlus.Core.WriteLine("I have the POWER!")
#Dictionary to hold relevant material values
Paras = dict.fromkeys([
        'name', 'diffuse', 'diffuse_roughness', 'selfIllumination', 'selfIllumination_gi', 'selfIllumination_multiplier',
        'reflection', 'reflection_glossiness', 'reflection_fresnel', 'reflection_maxDepth', 'reflection_exitColor',
        'reflection_useInterpolation', 'reflection_ior', 'refraction', 'refraction_glossiness', 'refraction_ior',
        'refraction_fogColor', 'refraction_affectAlpha', 'refraction_maxDepth', 'refraction_exitColor'
        'refraction_dispersion', 'refraction_dispersion_on', 'translucency_on', 'translucency_thickness',
        'translucency_scatterCoeff', 'translucency_fbCoeff', 'translucency_multiplier', 'translucency_color',
        'brdf_type', 'anisotropy', 'anistropy_rotation', 'anisotropy_derivation', 'anisotropy_axis' ,'anisotropy_channel'
        'soften', 'gtr_gamma', 'gtr_oldGamma', 'option_opacityMode'
        ])

myOrder = [
        'name', 'diffuse', 'diffuse_roughness', 'selfIllumination', 'selfIllumination_gi', 'selfIllumination_multiplier',
        'reflection', 'reflection_glossiness', 'reflection_fresnel', 'reflection_maxDepth', 'reflection_exitColor',
        'reflection_useInterpolation', 'reflection_ior', 'refraction', 'refraction_glossiness', 'refraction_ior',
        'refraction_fogColor', 'refraction_affectAlpha', 'refraction_maxDepth', 'refraction_exitColor'
        'refraction_dispersion', 'refraction_dispersion_on', 'translucency_on', 'translucency_thickness',
        'translucency_scatterCoeff', 'translucency_fbCoeff', 'translucency_multiplier', 'translucency_color',
        'brdf_type', 'anisotropy', 'anistropy_rotation', 'anisotropy_derivation', 'anisotropy_axis' ,'anisotropy_channel'
        'soften', 'gtr_gamma', 'gtr_oldGamma', 'option_opacityMode'
        ]

lightParas = {}
camParas = {}
myDuplicates = []

#Gets Scene Graph
def outputNode(n, indent = ''):
    #print indent, n.Name
    for c in n.Children:
        outputNode(c, indent + '--')

if __name__ == '__main__':
    outputNode(MaxPlus.Core.GetRootNode())

#This will return all the child nodes under the root scene node
def allNodes():
    return descendants(MaxPlus.Core.GetRootNode())

#This will get all the child nodes in the scene by name and memory address
def descendants(node):
    for c in node.Children:
        #print "Child: " + str(c)
        yield c
        for d in descendants(c):
            #print "Desc: " + str(d)
            yield d

def matGrab(tt):
    # Putting all the parameters together
    for p in tt.ParameterBlock.Parameters:
        if p.Name in Paras:
            x = p.Name
            Paras[str(x)] = str(p.Value)
    return Paras

def lightGrab(ll):
    # Putting all the parameters together
    for q in ll.ParameterBlock.Parameters:
        y = q.Name
        lightParas[str(y)] = str(q.Value)
    return lightParas

def camGrab(cc):
    # Putting all the parameters together
    for r in cc.ParameterBlock.Parameters:
        z = r.Name
        camParas[str(z)] = str(r.Value)
    return camParas

#Gets the mats from the the nodes in scene
def getVrayMaterialOnNodes(filePath, nodes = allNodes()):
    matPath = filePath
    matTextFile = open(matPath, 'w')
    sceneInJSON = ''
    i = 0
    for n in nodes:
        #print n.GetObject()
        if str(n.Material) == 'Animatable(VRayMtl)':
            tt = n.Material
            #Object Material properties stored to a dictionary
            Paras['name'] = tt.GetFullName()           #Displays Mat name and type

            #Adds to a duplicate list. For future filtering use
            myDuplicates.insert(i, Paras['name'])
            i += 1

            ParasMat = matGrab(tt)  # Call function to get parameters from mat
            # This code block below orders and preps the mat dict in the user specified format
            matParameters = OrderedDict((k, ParasMat[k]) for k in myOrder)
            matBaseName = str(n)
            matName, matID = matBaseName.split(',')
            matID = matID.replace("<", "")
            matID = matID.replace(">", "")
            matType = "Geometry"

            # after gathering all info for mat, add dumps to matInJSON
            sceneInJSON += "{\nINODE: {\nname: \"" + matName[7:] + "\"\nid: \"" + matID[1:] + "\"\ntype: \"" + \
                         matType + "\"\nmaterial: " + (json.dumps(matParameters, indent=4)) + \
                         ',\nPosition: {\n    "' + str(n.Position) + '"\n},\nRotation: {\n    "' + str(n.Rotation) + \
                         '"\n},\nScale: {\n    "' + str(n.Scale) + '"\n},\n}\n\n'

        if "Light" in str(n.GetObject()):
            # This code block below orders and preps the light dict in the user specified format
            ll = n.BaseObject
            lightBaseName = str(n)
            lightName, lightID = lightBaseName.split(',')
            lightID = lightID.replace("<", "")
            lightID = lightID.replace(">", "")

            ParasLight = lightGrab(ll)
            sceneInJSON += "{\nINODE: {\nname: \"" + lightName[7:] + "\"\nid: \"" + lightID[1:] + "\"\ntype: \"" + \
                         "Light" + "\"\nmaterial: " + (json.dumps(ParasLight, indent=4)) + \
                         ',\nPosition: {\n    "' + str(n.Position) + '"\n},\nRotation: {\n    "' + str(n.Rotation) + \
                         '"\n},\nScale: {\n    "' + str(n.Scale) + '"\n},\n}\n\n'


        if "Camera" in str(n.GetObject()):
            # This code block below orders and preps the cam dict in the user specified format
            cc = n.BaseObject
            camBaseName = str(n)
            camName, camID = camBaseName.split(',')
            camID = camID.replace("<", "")
            camID = camID.replace(">", "")

            ParasCam = camGrab(cc)
            sceneInJSON += "{\nINODE: {\nname: \"" + camName[7:] + "\"\nid: \"" + camID[1:] + "\"\ntype: \"" + \
                         "Light" + "\"\nmaterial: " + (json.dumps(ParasCam, indent=4)) + \
                         ',\nPosition: {\n    "' + str(n.Position) + '"\n},\nRotation: {\n    "' + str(n.Rotation) + \
                         '"\n},\nScale: {\n    "' + str(n.Scale) + '"\n},\n}\n\n'

    matTextFile.write(sceneInJSON)
    matTextFile.close()

def DoStuff():
    fm = MaxPlus.FileManager
    filePath = os.path.splitext(fm.GetFileNameAndPath())[0] + '.txt'
    print filePath
    getVrayMaterialOnNodes(filePath, nodes = allNodes())

DoStuff()
