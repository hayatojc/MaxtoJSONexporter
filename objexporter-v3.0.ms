macroScript MaxSceneExport
 Category:"MediaLab"
 toolTip:"MaxScene Export"
 buttontext:"MaxScene Export"
(
	exportFileName = substituteString maxFileName ".max" ".obj"
	exportfolderPath = maxfilepath
	
	rollout roll_MaxSceneExport "MaxSceneExport" width:512
	(
		label lbl1 "Export Path" align:#left
		edittext edt_ExportPath "" text:exportfolderPath
		label lbl2 "File Name" align:#left
		edittext edt_ExportFile "" text:exportFileName
		button btn_Export "Export"
		
		on btn_Export pressed do ( 
			
			-- Save current scene state
			holdMaxFile()
			
			-- create export path
			exportPathFull = exportfolderPath + exportFileName
			
			-- Create Exports folder if it doesn't exsist
			if doesFileExist exportfolderPath  == false do (
				makedir exportfolderPath
			)
		
			-- Reposition all objects
			--selection.position = [0,0,0]
			python.ExecuteFile @"I:\dev_JC\_Python\MaxExporter\MaxExporter_v4.py"
			
			-- Ritriangulate
			modPanel.addModToSelection (Turn_to_Poly ()) ui:on 
			for obj in selection do (
						obj.modifiers[#Turn_to_Poly].limitPolySize = on
			            obj.modifiers[#Turn_to_Poly].maxPolySize = 3
			)
			
			-- Exports the currently selected objects as fbx
			exportFile exportpathFull #noPrompt selectedOnly:false
 
			-- Restore scene
			fetchMaxFile quiet:true
			
		)
	)
	createdialog roll_MaxSceneExport
)