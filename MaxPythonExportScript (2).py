import MaxPlus
from collections import OrderedDict
import json
import os
import subprocess

#MaxPlus.Core.WriteLine("I have the POWER!")
#Dictionary to hold relevant material values
Paras = dict.fromkeys([
        'name', 'diffuse', 'diffuse_roughness', 'selfIllumination', 'selfIllumination_gi', 'selfIllumination_multiplier',
        'reflection', 'reflection_glossiness', 'reflection_fresnel', 'reflection_maxDepth', 'reflection_exitColor',
        'reflection_useInterpolation', 'reflection_ior', 'refraction', 'refraction_glossiness', 'refraction_ior',
        'refraction_fogColor', 'refraction_affectAlpha', 'refraction_maxDepth', 'refraction_exitColor'
        'refraction_dispersion', 'refraction_dispersion_on', 'translucency_on', 'translucency_thickness',
        'translucency_scatterCoeff', 'translucency_fbCoeff', 'translucency_multiplier', 'translucency_color',
        'brdf_type', 'anisotropy', 'anistropy_rotation', 'anisotropy_derivation', 'anisotropy_axis' ,'anistropy_channel',
        'soften', 'gtr_gamma', 'gtr_oldGamma', 'option_opacityMode', 'texmap_diffuse', 'texmap_roughness', 'texmap_reflection',
        'texmap_hilightGlossiness', 'texmap_reflectionGlossiness', 'texmap_refraction', 'texmap_refractionGlossiness', 'texmap_bump',
        'texmap_displacement', 'texmap_opacity'
        ])

myOrder = [
        'name', 'diffuse', 'diffuse_roughness', 'selfIllumination', 'selfIllumination_gi', 'selfIllumination_multiplier',
        'reflection', 'reflection_glossiness', 'reflection_fresnel', 'reflection_maxDepth', 'reflection_exitColor',
        'reflection_useInterpolation', 'reflection_ior', 'refraction', 'refraction_glossiness', 'refraction_ior',
        'refraction_fogColor', 'refraction_affectAlpha', 'refraction_maxDepth', 'refraction_exitColor'
        'refraction_dispersion', 'refraction_dispersion_on',
        'translucency_on', 'translucency_thickness', 'translucency_scatterCoeff', 'translucency_fbCoeff', 'translucency_multiplier',
        'translucency_color', 'brdf_type', 'anisotropy', 'anistropy_rotation', 'anisotropy_derivation', 'anisotropy_axis',
        'anistropy_channel', 'soften', 'gtr_gamma', 'gtr_oldGamma', 'option_opacityMode','texmap_diffuse',
        'texmap_roughness', 'texmap_reflection', 'texmap_hilightGlossiness', 'texmap_reflectionGlossiness',
        'texmap_refraction', 'texmap_refractionGlossiness', 'texmap_bump', 'texmap_displacement', 'texmap_opacity',
        ]
bitMap = dict.fromkeys([
         'name', 'fileName', 'preMultAlpha', 'mapChannel', 'mappingType', 'UVW_Type', 'U_Tile', 'V_Tile',
         'U_Offset', 'V_Offset', 'U_Tiling', 'V_Tiling'
         ])
texMapParamList = dict.fromkeys([
        'texmap_diffuse', 'texmap_roughness', 'texmap_reflection', 'texmap_hilightGlossiness', 'texmap_reflectionGlossiness',
        'texmap_refraction', 'texmap_refractionGlossiness', 'texmap_bump', 'texmap_displacement', 'texmap_opacity'
        ])
lightParas = {}
camParas = {}
myDuplicates = []
lights = ['Light', 'Target']
cameras = ['Camera', 'Target']

#Gets Scene Graph
def outputNode(n, indent = ''):
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

# Required to pull the data from a Materials Submaps aka Texmaps
def texMaps(tm):
    # Putting all the parameters together
    texParas = {}
    texMapParam = tm.GetParameterBlock()
    texParas['name'] = tm.GetFullName()
    texParas = collections.OrderedDict(texParas)

    # This is for getting parameters of a texmap depending on map type
    if hasattr(texMapParam, 'fileName'):    # Is it a bitmap?
        for z in texMapParam:
            if z.Name in bitMap:
                x = z.Name
                texParas[str(x)] = str(z.Value)
    else:
        for z in texMapParam:               # All other map types
            x = z.Name
            texParas[str(x)] = str(z.Value)


    # This is for getting parameters of the coords/outputs inside a bitmap.
    # Coords inside a bitmap are their own object
    try:    # This catch occurs if texmap is not a bitmap. Skips the for loop
        texCoords = texMapParam.coords.GetValue().GetParameterBlock()
        texBitMap = texMapParam.bitmap.GetValue().GetBitmapInfo().GetCustomGamma()
        texParas["Gamma"] = texBitMap
        for y in texCoords:
            if y.Name in bitMap:
                l = y.Name
                texParas[str(l)] = str(y.Value)

        # Ouput parameters of a bitmap
        texOutPut = texMapParam.output.GetValue().GetParameterBlock()
        for p in texOutPut:
            a = p.Name
            texParas[str(a)] = str(p.Value)
    except RuntimeError:
        print "Runtime Error: This Parameter does not exist."

    return texParas

# Required to JSON format the Materials
def formatMats(fm,n1):
    # This code block below orders and preps the mat dict in the user specified format
    matParameters = OrderedDict((k, fm[k]) for k in myOrder)
    matBaseName = str(n1)
    matName, matID = matBaseName.split(',')
    matID = matID.replace("<", "")
    matID = matID.replace(">", "")
    matType = "Geometry"

    # after gathering all info for mat, add dumps to matInJSON
    jsonS = ""
    sceneInJ = ""
    sceneInJ += jsonS + "{\nname: \"" + matName[7:] + "\",\nid: \"" + matID[1:] + "\",\ntype: \"" + \
                   matType + "\",\nmaterial: " + (json.dumps(matParameters, indent=4))
    return sceneInJ

# Required to JSON format the submaps in a Material
def formatTexMap(tm1, tm2):
    # This code block below orders and preps the mat dict in the user specified format
    texParameters = tm1
    jsonS = "\n" + tm2 + ": "
    sceneInJ = jsonS + (json.dumps(texParameters, indent=4))
    return sceneInJ

#Gets the mats from the the nodes in scene
def getVrayMaterialOnNodes(filePath, nodes = allNodes()):
    matPath = filePath
    matTextFile = open(matPath, 'w')
    sceneInJSON = '[\n'
    i = 0
    jsonStart = ""

    for n in nodes:
        print n
        print str(n.GetObject())

        bShouldFinalizeNode = 0

        # Handles data pull of any material
        if str(n.Material) == 'Animatable(VRayMtl)':
            bShouldFinalizeNode = 1
            tt = n.Material
            #Object Material properties stored to a dictionary
            Paras['name'] = tt.GetFullName()           #Displays Mat name and type

            #Adds to a duplicate list. For future filtering use
            myDuplicates.insert(i, Paras['name'])
            i += 1
            ParasMat = matGrab(tt)  # Call function to get parameters from mat

            sceneInJSON += formatMats(ParasMat, n)

            # Process SubMaps
            try:
                for v in tt.ParameterBlock.Parameters:
                    if v.Name in texMapParamList:
                        currentMap = v.Name
                        currentValue = v.Value
                        texValue = texMaps(currentValue)
                        sceneInJSON += formatTexMap(texValue, currentMap)
            except:
                print "No texmaps found on this go"

        # Handles data pull of any light
        if "Light" in str(n.GetObject()):
            bShouldFinalizeNode = 1
            # This code block below orders and preps the light dict in the user specified format
            ll = n.BaseObject
            lightBaseName = str(n)
            lightName, lightID = lightBaseName.split(',')
            lightID = lightID.replace("<", "")
            lightID = lightID.replace(">", "")

            ParasLight = lightGrab(ll)
            sceneInJSON += jsonStart + "{\nname: \"" + lightName[7:] + "\",\nid: \"" + lightID[1:] + "\",\ntype: \"" + \
                         "Light" + "\",\nparams: " + (json.dumps(ParasLight, indent=4))

        # Handles data pull on any camera target
        if "Target" in str(n.GetObject()):
            bShouldFinalizeNode = 1
            # This code block below orders and preps the light dict in the user specified format
            targetBaseName = str(n)
            targetName, targetID = targetBaseName.split(',')
            targetID = targetID.replace("<", "")
            targetID = targetID.replace(">", "")

            sceneInJSON += jsonStart + "{\nname: \"" + targetName[7:] + "\",\nid: \"" + targetID[1:] + "\",\ntype: \"" + \
                           "Target\""

        # Handles data pull on any camera
        if "Camera" in str(n.GetObject()):
            bShouldFinalizeNode = 1
            cc = n.BaseObject
            camBaseName = str(n)
            camName, camID = camBaseName.split(',')
            camID = camID.replace("<", "")
            camID = camID.replace(">", "")

            ParasCam = camGrab(cc)
            sceneInJSON += jsonStart + "{\nname: \"" + camName[7:] + "\",\nid: \"" + camID[1:] + "\",\ntype: \"" + \
                         "Camera" + "\",\nparams: " + (json.dumps(ParasCam, indent=4))
        
        # this code block finished up the common properties of all nodes
        if bShouldFinalizeNode == 1: 
            euler = n.Rotation.GetEuler()
            sceneInJSON += ',\nPosition:"' + str(n.Position) + '",\nRotationEuler:"' + str(euler)+ '",\nRotationQuat:"' + str(n.Rotation) + \
                         '",\nScale:{}' + '\n}'
      
        jsonStart = ",\n\n"

    sceneInJSON += "]"
    print sceneInJSON
    matTextFile.write(sceneInJSON)
    matTextFile.close()
    
def executeAssetDeployment(objFilePath, jsonFilePath, destinationFolderPath):
    exeFilePath = "C:\\tfs_rd\\RayTracer\\Csharp\\MediaLab.RayTracer.Csharp\\MediaLab.PT.AssetDeploymentCmdLine\\bin\\Debug\\MediaLab.PT.AssetDeploymentCmdLine.exe"
    #exeFilePath = "I:\\R&D\\scripts\\maxscenetojson\\AssetDeployer\\MediaLab.PT.AssetDeploymentCmdLine.exe"
    returncode = subprocess.call([exeFilePath, objFilePath, jsonFilePath, destinationFolderPath])
    print "asset deployment program path:" + exeFilePath
    print "deployment program exit code: " + str(returncode)
    print "json file path: " + jsonFilePath
    print "obj file path: " + objFilePath
    print "deployed to: " + destinationFolderPath

def runProgram():
    fm = MaxPlus.FileManager
   
    # get file paths from OS GUI
    filePaths = (MaxPlus.Core.EvalMAXScript('exportPathFull'))
    objFilePath = MaxPlus.FPValue.Get(filePaths)
    jsonFilePath = objFilePath.replace("obj", "json")
   
    # destinationFolderPath = "C:\\tfs_rd\\RayTracer\\WebGL\\VisualTests\\raytracer\\assets"
    # deploy processed assets to same directory as the obj and json files
    destinationFolderPath = os.path.dirname(objFilePath)
   
    # extract vray information from 3dmax
    getVrayMaterialOnNodes(jsonFilePath, nodes = allNodes())
  
    # call external deployment program to further process the obj and json files, 
    # then deploy them to the destination directory
    executeAssetDeployment(objFilePath, jsonFilePath, destinationFolderPath)

runProgram()
