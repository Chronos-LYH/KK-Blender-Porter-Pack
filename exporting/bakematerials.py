'''
BAKE MATERIAL TO TEXTURE SCRIPT
- Bakes all materials of an object into image textures (to use in other programs)
- Will only bake a material if an image node is present in the green texture group
- If no image is present, a low resolution failsafe image will be baked to account for fully opaque or transparent materials that don't rely on texture files
- If multiple image files are present, only one texture will be created
    - If the multiple image files have different resolutions, a texture will be created for each resolution
- Export defaults to 8-bit PNG with an alpha channel.
--    Defaults can be changed by editing the exportType and exportColormode variables below.
- Creates a material atlas and applies it to a copy of the model

Notes:
- This script deletes all camera objects in the scene
- fillerplane driver + shader code taken from https://blenderartists.org/t/scripts-create-camera-image-plane/580839
- material combiner code taken from https://github.com/Grim-es/material-combiner-addon/
'''

import bpy, os, traceback, time, pathlib, subprocess
from .. import common as c
from ..interface.dictionary_en import t

def print_memory_usage(stri):
    run = subprocess.run('wmic OS get FreePhysicalMemory', capture_output=True)
    c.kklog((stri, '\n   mem usage ', 16000 - int(run.stdout.split(b'\r')[2].split(b'\n')[1])/1000))

def showError(self, context):
    self.layout.label(text="No object selected (make sure the body object is selected)")

def typeError(self, context):
    self.layout.label(text="The object to bake must be a mesh object (make sure the body object is selected)")

#setup and return a camera
def setup_camera():
    #Delete all cameras in the scene
    for obj in bpy.context.scene.objects:
        if obj.type == 'CAMERA':
            obj.select_set(True)
        else:
            obj.select_set(False)
    bpy.ops.object.delete()
    for block in bpy.data.cameras:
        if block.users == 0:
            bpy.data.cameras.remove(block)
   
    #Add a new camera
    bpy.ops.object.camera_add(enter_editmode=False, align='VIEW', location=(0, 0, 1), rotation=(0, 0, 0))
    #save it for later
    camera = bpy.context.active_object
    #and set it as the active one
    bpy.context.scene.camera=camera
    #Set camera to orthographic
    bpy.data.cameras[camera.name].type='ORTHO'
    bpy.data.cameras[camera.name].ortho_scale=6
    bpy.context.scene.render.pixel_aspect_y=1
    bpy.context.scene.render.pixel_aspect_x=1
    return camera

def setup_geometry_nodes_and_fillerplane(camera):
    object_to_bake = bpy.context.active_object

    #create fillerplane
    bpy.ops.mesh.primitive_plane_add()
    bpy.ops.object.material_slot_add()
    fillerplane = bpy.context.active_object
    fillerplane.data.uv_layers[0].name = 'uv_main'
    fillerplane.name = "fillerplane"
    bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.transform.resize(value=(0.5,0.5,0.5))
    bpy.ops.uv.reset()
    bpy.ops.object.editmode_toggle()

    fillerplane.location = (0,0,-0.0001)

    def setup_driver_variables(driver, camera):
        cam_ortho_scale = driver.variables.new()
        cam_ortho_scale.name = 'cOS'
        cam_ortho_scale.type = 'SINGLE_PROP'
        cam_ortho_scale.targets[0].id_type = 'CAMERA'
        cam_ortho_scale.targets[0].id = bpy.data.cameras[camera.name]
        cam_ortho_scale.targets[0].data_path = 'ortho_scale'
        resolution_x = driver.variables.new()
        resolution_x.name = 'r_x'
        resolution_x.type = 'SINGLE_PROP'
        resolution_x.targets[0].id_type = 'SCENE'
        resolution_x.targets[0].id = bpy.context.scene
        resolution_x.targets[0].data_path = 'render.resolution_x'
        resolution_y = driver.variables.new()
        resolution_y.name = 'r_y'
        resolution_y.type = 'SINGLE_PROP'
        resolution_y.targets[0].id_type = 'SCENE'
        resolution_y.targets[0].id = bpy.context.scene
        resolution_y.targets[0].data_path = 'render.resolution_y'
    
    #setup X scale for bake object and plane
    # print(object_to_bake)
    driver = object_to_bake.driver_add('scale',0).driver
    driver.type = 'SCRIPTED'
    setup_driver_variables(driver, camera)
    driver.expression = "((r_x)/(r_y)*(cOS)) if (((r_x)/(r_y)) < 1) else (cOS)"

    driver = fillerplane.driver_add('scale',0).driver
    driver.type = 'SCRIPTED'
    setup_driver_variables(driver, camera)
    driver.expression = "((r_x)/(r_y)*(cOS)) if (((r_x)/(r_y)) < 1) else (cOS)"

    #setup drivers for object's Y scale
    driver = object_to_bake.driver_add('scale',1).driver
    driver.type = 'SCRIPTED'
    setup_driver_variables(driver, camera)
    driver.expression = "((r_y)/(r_x)*(cOS)) if (((r_y)/(r_x)) < 1) else (cOS)"

    driver = fillerplane.driver_add('scale',1).driver
    driver.type = 'SCRIPTED'
    setup_driver_variables(driver, camera)
    driver.expression = "((r_y)/(r_x)*(cOS)) if (((r_y)/(r_x)) < 1) else (cOS)"

    ###########################
    #import the premade flattener node to unwrap the mesh into the UV structure
    script_dir=pathlib.Path(__file__).parent
    template_path=(script_dir / '../KK Shader V7.0.blend').resolve()
    filepath = str(template_path)
    innerpath = 'NodeTree'
    geonodename = 'Geometry Nodes'
    bpy.ops.wm.append(
            filepath=os.path.join(filepath, innerpath, geonodename),
            directory=os.path.join(filepath, innerpath),
            filename=geonodename
            )

    #give the object a geometry node modifier
    geonodes_mod = object_to_bake.modifiers.new('Flattener', 'NODES')
    geonodes_mod.node_group = bpy.data.node_groups['Geometry Nodes']
    identifier = [str(i) for i in geonodes_mod.keys()][0]
    geonodes_mod[identifier+'_attribute_name'] = 'uv_main'
    geonodes_mod[identifier+'_use_attribute'] = True

    #Make the originally selected object active again
    bpy.ops.object.select_all(action='DESELECT')
    object_to_bake.select_set(True)
    bpy.context.view_layer.objects.active=object_to_bake

##############################
#Changes the material of the image plane to the material of the object,
# and then puts a render of the image plane into the specified folder

def sanitizeMaterialName(text):
    '''Mat names need to be sanitized else you can't delete the files with windows explorer'''
    for ch in ['\\','`','*','<','>','.',':','?','|','/','\"']:
        if ch in text:
            text = text.replace(ch,'')
    return text

def bake_pass(resolutionMultiplier, folderpath, bake_type):
    #get list of already baked files
    fileList = pathlib.Path(folderpath).glob('*.*')
    files = [file for file in fileList if file.is_file()]
    #print(files)
    exportType = 'PNG'
    exportColormode = 'RGBA'
    #get the currently selected object as the active object
    object_to_bake = bpy.context.active_object
    #remember what order the materials are in for later
    original_material_order = []
    for matslot in object_to_bake.material_slots:
        original_material_order.append(matslot.name)
    #get the filler plane
    fillerplane = bpy.data.objects['fillerplane']

    #if this is a light or dark pass, make sure the RawShade group is a constant light or dark
    if bake_type in ['light', 'dark']:
        raw = bpy.data.node_groups['Raw Shading']
        getOut = raw.nodes['breaknode'].inputs[6].links[0]
        raw.links.remove(getOut)
        raw.nodes['breaknode'].inputs[6].default_value = (1,1,1,1) if bake_type == 'light' else (0,0,0,1)

    #go through each material slot
    for index, currentmaterial in enumerate(object_to_bake.data.materials):
        nodes = currentmaterial.node_tree.nodes
        links = currentmaterial.node_tree.links

        #print(currentmaterial)
        #Don't bake this material if it doesn't have the 'baked_group' slot
        if not currentmaterial.node_tree.nodes.get('baked_group'):
            c.kklog(f'Skipping {currentmaterial.name} because it does not have a baked_group slot')
            continue

        #Don't bake this material if it's an outline material or atlas material
        if 'Outline ' in currentmaterial.name or 'KK Outline' in currentmaterial.name or 'KK Body Outline' in currentmaterial.name or ' Atlas' in currentmaterial.name:
            c.kklog(f'Skipping {currentmaterial.name} because it is an atlas or outline material')
            continue

        #Don't bake this material if it is a simplified material
        if bpy.data.materials.get(currentmaterial.name + '-ORG'):
            c.kklog(f'Skipping {currentmaterial.name} because it is a simplified material')
            continue

        #Don't bake this material if the material already has the atlas nodes loaded in and the mix shader is set to 1 and the image already exists (user is re-baking a mat)
        if currentmaterial.node_tree.nodes.get('baked_group'):
            if currentmaterial.node_tree.nodes['baked_group'].inputs[3].default_value > 0.5 and pathlib.Path(folderpath + sanitizeMaterialName(currentmaterial.name) + ' ' + bake_type + '.png') in files:
                c.kklog(f'Skipping {currentmaterial.name} {bake_type} because it already exists')
                continue
            else:
                currentmaterial.node_tree.nodes['baked_group'].inputs[3].default_value = 0
        
        #Turn off the normals for the raw shading node group input if this isn't a normal pass
        if nodes.get('RawShade') and bake_type != 'normal':
            original_normal_state = nodes['RawShade'].inputs[1].default_value
            nodes['RawShade'].inputs[1].default_value = 1
        
        #if this is a normal pass, attach the normal passthrough to the output before baking
        if nodes.get('RawShade') and bake_type == 'normal':
            getOut = nodes['Material Output'].inputs[0].links[0]
            currentmaterial.node_tree.links.remove(getOut)
            links.new(nodes['RawShade'].outputs[1], nodes['Material Output'].inputs[0])

        rendered_something = False

        if nodes.get('Gentex'):
            #Go through each of the textures loaded into the Gentex group and get the highest resolution one
            highest_resolution = [0,0]
            for image_node in nodes['Gentex'].node_tree.nodes:
                if image_node.type == 'TEX_IMAGE' and image_node.image:
                    image_size = image_node.image.size[0] * image_node.image.size[1]
                    largest_so_far = highest_resolution[0] * highest_resolution[1]
                    if image_size > largest_so_far:
                        highest_resolution = [image_node.image.size[0], image_node.image.size[1]]
            
            #Render an image using the highest dimensions
            if highest_resolution != [0,0]:
                bpy.context.scene.render.resolution_x=highest_resolution[0] * resolutionMultiplier
                bpy.context.scene.render.resolution_y=highest_resolution[1] * resolutionMultiplier

                #manually set gag02 resolution
                if 'KK Gag02' in currentmaterial.name:
                    bpy.context.scene.render.resolution_x = 512 * resolutionMultiplier
                    bpy.context.scene.render.resolution_y = 512 * resolutionMultiplier

                #set every material slot except the current material to be transparent
                for matslot in object_to_bake.material_slots:
                    if matslot.material != currentmaterial:
                        matslot.material = bpy.data.materials['KK Eyeline down']
                
                #set the filler plane to the current material
                fillerplane.material_slots[0].material = currentmaterial

                #then render it
                matname = sanitizeMaterialName(currentmaterial.name)
                matname = matname[:-4] if matname[-4:] == '-ORG' else matname
                bpy.context.scene.render.filepath = folderpath + matname + ' ' + bake_type
                bpy.context.scene.render.image_settings.file_format=exportType
                bpy.context.scene.render.image_settings.color_mode=exportColormode
                #bpy.context.scene.render.image_settings.color_depth='16'
                
                #bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
                # print('rendering this file:' + bpy.context.scene.render.filepath)
                print('Rendering {} / {}'.format(index+1, len(object_to_bake.data.materials)))
                bpy.ops.render.render(write_still = True)
                
                #reset folderpath after render
                bpy.context.scene.render.filepath = folderpath

                rendered_something = True

                #redraw the UI to let the user know the plugin is doing something
                #bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)

        #If no images were detected in a Gentex group, render a very small (64px) failsafe image
        #this will let the script catch fully transparent materials or materials that are solid colors without textures
        if not rendered_something:
            bpy.context.scene.render.resolution_x=64
            bpy.context.scene.render.resolution_y=64
            
            #set every material slot except the current material to be transparent
            for matslot in object_to_bake.material_slots:
                if matslot.material != currentmaterial:
                    #print("changed {} to {}".format(matslot.material, currentmaterial))
                    matslot.material = bpy.data.materials['KK Eyeline down']

            #set the filler plane to the current material
            fillerplane.material_slots[0].material = currentmaterial

            #then render it
            bpy.context.scene.render.filepath = folderpath + sanitizeMaterialName(currentmaterial.name) + ' ' + bake_type
            bpy.context.scene.render.image_settings.file_format=exportType
            bpy.context.scene.render.image_settings.color_mode=exportColormode
            #bpy.context.scene.render.image_settings.color_depth='16'
            
            #bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
            # print('rendering failsafe for this file:' + bpy.context.scene.render.filepath)
            bpy.ops.render.render(write_still = True)
            #print(fillerplane.data.materials[0])
            
            #reset folderpath after render
            bpy.context.scene.render.filepath = folderpath
        
        #Restore the value in the raw shading node group for the normals
        if currentmaterial.node_tree.nodes.get('RawShade') and bake_type != 'normal':
            currentmaterial.node_tree.nodes['RawShade'].inputs[1].default_value = original_normal_state
        
        #Restore the links if they were edited for the normal pass
        if currentmaterial.node_tree.nodes.get('RawShade') and bake_type == 'normal':
            getOut = nodes['Material Output'].inputs[0].links[0]
            currentmaterial.node_tree.links.remove(getOut)
            if nodes.get('baked_group'):
                links.new(nodes['baked_group'].outputs[0], nodes['Material Output'].inputs[0])
            else:
                links.new(nodes['Rim'].outputs[0], nodes['Material Output'].inputs[0])
        #reset material slots
        for material_index in range(len(original_material_order)):
            object_to_bake.material_slots[material_index].material = bpy.data.materials[original_material_order[material_index]]
    
    #reset raw shading group state
    if bake_type in ['light', 'dark']:
        raw.links.new(raw.nodes['breakreroute'].outputs[0], raw.nodes['breaknode'].inputs[6])

def start_baking(folderpath, resolutionMultiplier, light, dark, norm):
    #enable transparency
    bpy.context.scene.render.film_transparent = True
    bpy.context.scene.render.filter_size = 0.50
    
    object_to_bake = bpy.context.active_object
    #Purge unused lights
    for block in bpy.data.lights:
        if block.users == 0:
            bpy.data.lights.remove(block)

    #Make a new sun object
    #bpy.ops.object.light_add(type='SUN', radius=1, align='WORLD', location=(0, 0, 0)) #no longer need the sun object

    #Make the originally selected object active again
    bpy.ops.object.select_all(action='DESELECT')
    object_to_bake.select_set(True)
    bpy.context.view_layer.objects.active=object_to_bake

    if light:
        #bake the light versions of each material to the selected folder at sun intensity 5
        bake_pass(resolutionMultiplier, folderpath, 'light')
    
    if dark:
        #bake the dark versions of each material at sun intensity 0
        bake_pass(resolutionMultiplier, folderpath, 'dark')
    
    if norm:
        #bake the normal maps
        bake_pass(resolutionMultiplier, folderpath, 'normal')

    #Make the originally selected object active again
    bpy.ops.object.select_all(action='DESELECT')
    object_to_bake.select_set(True)
    bpy.context.view_layer.objects.active=object_to_bake

def cleanup():
    # Deselect all objects
    bpy.ops.object.select_all(action='DESELECT')
    #Select the camera
    for camera in [o for o in bpy.data.objects if o.type == 'CAMERA']:
        bpy.data.objects.remove(camera)
    #Select fillerplane
    for fillerplane in [o for o in bpy.data.objects if 'fillerplane' in o.name]:
        bpy.data.objects.remove(fillerplane)
    #delete orphan data
    for block in bpy.data.meshes:
        if block.users == 0:
            bpy.data.meshes.remove(block)
    for block in bpy.data.cameras:
        if block.users == 0:
            bpy.data.cameras.remove(block)
    for ob in [obj for obj in bpy.context.view_layer.objects]:
        if ob: #getting a weird Nonetype error, so do it this way instead
            if ob.type == 'MESH':
                #delete the geometry modifier
                if ob.modifiers.get('Flattener'):
                    ob.modifiers.remove(ob.modifiers['Flattener'])
                    #delete the two scale drivers
                    ob.animation_data.drivers.remove(ob.animation_data.drivers[0])
                    ob.animation_data.drivers.remove(ob.animation_data.drivers[0])
                    ob.scale = (1,1,1)
    bpy.data.node_groups.remove(bpy.data.node_groups['Geometry Nodes'])
    #disable alpha on the output
    bpy.context.scene.render.film_transparent = False
    bpy.context.scene.render.filter_size = 1.5

def replace_all_baked_materials(folderpath):
    
    #load all baked images into blender
    fileList = pathlib.Path(folderpath).glob('*.*')
    files = [file for file in fileList if file.is_file()]
    print(files)
    print('----------------')
    for bake_type in ['light', 'dark', 'normal']:
        for mat in [m for m in bpy.data.materials if 'KK ' in m.name and 'Outline ' not in m.name and ' Outline' not in m.name and ' Atlas' not in m.name]:
            matname = mat.name[:-4] if mat.name[-4:] == '-ORG' else mat.name
            image_path = pathlib.Path(folderpath + '/' + sanitizeMaterialName(matname) + ' ' + bake_type + '.png')
            print(image_path)
            if image_path in files:
                image = bpy.data.images.load(filepath=str(image_path))
                image.pack()
                #if there was an older version of this image, get rid of it
                if image.name[-4:] == '.001':
                    if bpy.data.images.get(image.name[:-4]):
                        bpy.data.images[image.name[:-4]].user_remap(image)
                        bpy.data.images.remove(bpy.data.images[image.name[:-4]])
                        image.name = image.name[:-4]

    #now all needed images are loaded into the file. Match each material to it's image textures
    for mat in [m for m in bpy.data.materials if m.name not in ['KK Simple', "KK Tears", "KK Shadowcast", "KK Gag02", "KK Gag01", "KK Gag00"]]:
        finalize_this_mat = 'KK ' in mat.name and 'Outline ' not in mat.name and ' Outline' not in mat.name and ' Atlas' not in mat.name
        if finalize_this_mat:
            matname = mat.name[:-4] if mat.name[-4:] == '-ORG' else mat.name
            if mat.node_tree.nodes.get('baked_file'):
                if not mat.node_tree.nodes['baked_file'].image:
                    c.kklog('loading in image that was missed {}'.format(matname + ' light.png'))
                    try:
                        mat.node_tree.nodes['baked_file'].image = bpy.data.images[matname + ' light.png']
                        mat.node_tree.nodes['baked_group'].inputs[3].default_value = 1
                    except:
                        try:
                            mat.node_tree.nodes['baked_file'].image = bpy.data.images[matname + ' dark.png']
                            mat.node_tree.nodes['baked_group'].inputs[3].default_value = 1
                        except:
                            c.kklog('Could not finalize {}'.format(mat), 'warn')
                if mat.node_tree.nodes['baked_file'].image:
                    mat.node_tree.nodes['baked_group'].inputs[3].default_value = 1
                    if ' light.png' in mat.node_tree.nodes['baked_file'].image.name:
                        light_image = mat.node_tree.nodes['baked_file'].image.name
                        dark_image  = mat.node_tree.nodes['baked_file'].image.name.replace('light', 'dark')
                        normal_image  = mat.node_tree.nodes['baked_file'].image.name.replace('light', 'normal')
                    else:
                        dark_image = mat.node_tree.nodes['baked_file'].image.name
                        light_image  = mat.node_tree.nodes['baked_file'].image.name.replace('dark', 'light')
                        normal_image  = mat.node_tree.nodes['baked_file'].image.name.replace('dark', 'normal')
                    #mat_dict[matname] = [light_image, dark_image]

                    #rename material to -ORG, and replace it with a new material
                    mat.name += '-ORG' if '-ORG' not in mat.name else ''
                    try:
                        simple = bpy.data.materials['KK Simple'].copy()
                    except:
                        script_dir=pathlib.Path(__file__).parent
                        template_path=(script_dir / '../KK Shader V7.0.blend').resolve()
                        filepath = str(template_path)
                        innerpath = 'Material'
                        templateList = ['KK Simple']
                        for template in templateList:
                            bpy.ops.wm.append(
                                filepath=os.path.join(filepath, innerpath, template),
                                directory=os.path.join(filepath, innerpath),
                                filename=template,
                                set_fake=False
                                )
                        simple = bpy.data.materials['KK Simple'].copy()
                    simple.name = mat.name.replace('-ORG','')
                    new_node = simple.node_tree.nodes['Gentex'].node_tree.copy()
                    simple.node_tree.nodes['Gentex'].node_tree = new_node
                    new_node.name = simple.name
                    new_node.nodes['light'].image = bpy.data.images[light_image]
                    if bpy.data.images.get(dark_image):
                        print('Loaded ', dark_image)
                        new_node.nodes['dark'].image = bpy.data.images[dark_image]
                    if bpy.data.images.get(normal_image):
                        new_node.nodes['normal'].image = bpy.data.images[normal_image]
                    #replace instances of ORG material with new finalized one
                    mat.use_fake_user = True
                    alpha_blend_mats = [
                        'KK Nose',
                        'KK Eyebrows (mayuge)',
                        'KK Eyeline up',
                        'KK Eyeline Kage',
                        'KK Eyeline down',
                        'KK EyewhitesL (sirome)',
                        'KK EyewhitesR (sirome)',
                        'KK EyeL (hitomi)',
                        'KK EyeR (hitomi)']
                    for obj in bpy.data.objects:
                        for mat_slot in obj.material_slots:
                            if mat_slot.name.replace('-ORG','') == simple.name:
                                mat_slot.material = simple
                                if simple.name in alpha_blend_mats:
                                    mat_slot.material.blend_method = 'BLEND'
                    
                    #load the lbs simple shader if using lbs
                    if bpy.context.scene.kkbp.shader_dropdown == 'C':
                        try:
                            lbs_simple = bpy.data.node_groups['Simple Shader (LBS)'].copy()
                        except:
                            script_dir=pathlib.Path(__file__).parent
                            template_path=(script_dir / '../KK Shader V7.0.blend').resolve()
                            filepath = str(template_path)
                            innerpath = 'NodeTree'
                            templateList = ['Simple Shader (LBS)']
                            for template in templateList:
                                bpy.ops.wm.append(
                                    filepath=os.path.join(filepath, innerpath, template),
                                    directory=os.path.join(filepath, innerpath),
                                    filename=template,
                                    set_fake=False
                                    )
                            lbs_simple = bpy.data.node_groups['Simple Shader (LBS)'].copy()

                        if mat.name not in alpha_blend_mats:
                            simple.node_tree.nodes['Shader'].node_tree = lbs_simple
                        
def create_material_atlas(folderpath):
    '''Merges all the finalized material png files into a single atlas file, copies the current model and applies the atlas to the copy'''
    # https://blender.stackexchange.com/questions/127403/change-active-collection
    #Recursivly transverse layer_collection for a particular name
    def recurLayerCollection(layerColl, collName):
        found = None
        if (layerColl.name == collName):
            return layerColl
        for layer in layerColl.children:
            found = recurLayerCollection(layer, collName)
            if found:
                return found
    
    def remove_orphan_data():
        #revert the image back from the atlas file to the baked file   
        for mat in bpy.data.materials:
            # print(mat.name)
            if mat.name[-4:] == '-ORG':
                simplified_name = mat.name[:-4]
                if bpy.data.materials.get(simplified_name):
                    simplified_mat = bpy.data.materials[simplified_name]
                    for bake_type in ['light', 'dark', 'normal']:
                        simplified_mat.node_tree.nodes['Gentex'].node_tree.nodes[bake_type].image = bpy.data.images.get(simplified_name + ' ' + bake_type + '.png')
        #delete orphan data
        for cat in [bpy.data.armatures, bpy.data.objects, bpy.data.meshes, bpy.data.materials, bpy.data.images, bpy.data.node_groups]:
            for block in cat:
                if block.users == 0:
                    cat.remove(block)

    if bpy.data.collections.get('Model with atlas'):
        print('deleting previous collection "Model with atlas" and regenerating atlas model...')
        def del_collection(coll):
            for c in coll.children:
                del_collection(c)
            bpy.data.collections.remove(coll,do_unlink=True)
        del_collection(bpy.data.collections["Model with atlas"])
        remove_orphan_data()
        #show the original collection again
        layer_collection = bpy.context.view_layer.layer_collection
        layerColl = recurLayerCollection(layer_collection, 'Scene Collection')
        bpy.context.view_layer.active_layer_collection = layerColl
        bpy.context.scene.view_layers[0].active_layer_collection.children[0].exclude = False

    #Change the Active LayerCollection to 'My Collection'
    layer_collection = bpy.context.view_layer.layer_collection
    layerColl = recurLayerCollection(layer_collection, 'Collection')
    bpy.context.view_layer.active_layer_collection = layerColl

    # https://blender.stackexchange.com/questions/157828/how-to-duplicate-a-certain-collection-using-python
    from collections import  defaultdict
    def copy_objects(from_col, to_col, linked, dupe_lut):
        for o in from_col.objects:
            dupe = o.copy()
            if not linked and o.data:
                dupe.data = dupe.data.copy()
            to_col.objects.link(dupe)
            dupe_lut[o] = dupe
    def copy(parent, collection, linked=False):
        dupe_lut = defaultdict(lambda : None)
        def _copy(parent, collection, linked=False):
            cc = bpy.data.collections.new(collection.name)
            copy_objects(collection, cc, linked, dupe_lut)
            for c in collection.children:
                _copy(cc, c, linked)
            parent.children.link(cc)
        _copy(parent, collection, linked)
        # print(dupe_lut)
        for o, dupe in tuple(dupe_lut.items()):
            parent = dupe_lut[o.parent]
            if parent:
                dupe.parent = parent
    context = bpy.context
    scene = context.scene
    col = context.collection
    # print(col, scene.collection)
    assert(col is not scene.collection)
    copy(scene.collection, col)

    #setup materials for the combiner script
    for obj in [o for o in bpy.data.collections['Collection.001'].all_objects if not o.hide_get() and o.type == 'MESH']:
        for mat in [mat_slot.material for mat_slot in obj.material_slots if 'KK ' in mat_slot.material.name and 'Outline ' not in mat_slot.material.name and ' Outline' not in mat_slot.material.name and ' Atlas' not in mat_slot.material.name]:
            if bpy.data.materials.get(mat.name + '-ORG'):
                print('adding emission to {}'.format(mat))
                #this is a simple material
                nodes = mat.node_tree.nodes
                links = mat.node_tree.links
                emissive_node = nodes.new('ShaderNodeEmission')
                emissive_node.name = 'Emission'
                image_node = nodes.new('ShaderNodeTexImage')
                image_node.name = 'Image Texture'
                links.new(emissive_node.inputs[0], image_node.outputs[0])
                image_node.image = nodes['Gentex'].node_tree.nodes['light'].image
        context.view_layer.objects.active = obj
        bpy.ops.object.material_slot_remove_unused()

    #call the material combiner script
    bpy.ops.kkbp.combiner()

    #replace all images with the atlas in a new atlas material
    bake_types = []
    if scene.kkbp.bake_light_bool:
        bake_types.append('light')
    if scene.kkbp.bake_dark_bool:
        bake_types.append('dark')
    if scene.kkbp.bake_norm_bool:
        bake_types.append('normal')
    for index, obj in enumerate([o for o in bpy.data.collections['Collection.001'].all_objects if not o.hide_get() and o.type == 'MESH']):
        #disable the outline on the atlased object because I don't feel like fixing it
        if obj.modifiers.get('Outline Modifier'):
            obj.modifiers['Outline Modifier'].show_render = False
            obj.modifiers['Outline Modifier'].show_viewport = False
        #fix the armature modifier
        if obj.modifiers[0].type == 'ARMATURE':
            obj.modifiers[0].object = bpy.data.objects["Armature.001"]
        for bake_type in bake_types:
            #check for atlas dupes
            if bpy.data.images.get(f'{index}_{bake_type}.png'):
                bpy.data.images.remove(bpy.data.images.get(f'{index}_{bake_type}.png'))
            atlas_image = bpy.data.images.load(os.path.join(context.scene.kkbp.import_dir, 'atlas_files', f'{index}_{bake_type}.png'))
            for material in [mat_slot.material for mat_slot in obj.material_slots if 'KK ' in mat_slot.name and 'Outline ' not in mat_slot.name and ' Outline' not in mat_slot.name and ' Atlas' not in mat_slot.name]:
                if bpy.data.materials.get(material.name + '-ORG'):
                    image = None
                    try:
                        image = material.node_tree.nodes['Gentex'].node_tree.nodes[bake_type].image
                        if image.name == 'Template: Pattern Placeholder':
                            image = None
                    except:
                        image = None
                    if not image:
                        continue
                    else:
                        if not bpy.data.materials.get('{} Atlas'.format(material.name)):
                            #remove the emission nodes from earlier
                            if material.node_tree.nodes.get('Emission'):
                                material.node_tree.nodes.remove(material.node_tree.nodes['Image Texture'])
                                material.node_tree.nodes.remove(material.node_tree.nodes['Emission'])
                            atlas_material = material.copy()
                            atlas_material.name = '{} Atlas'.format(material.name)
                            new_group = atlas_material.node_tree.nodes['Gentex'].node_tree.copy()
                            new_group.name = '{} Atlas'.format(material.name)
                        else:
                            atlas_material =  bpy.data.materials.get('{} Atlas'.format(material.name))
                            new_group = bpy.data.node_groups.get('{} Atlas'.format(material.name))
                        atlas_material.node_tree.nodes['Gentex'].node_tree = new_group
                        new_group.nodes[bake_type].image = atlas_image

        #replace all images with the atlas in a new atlas material
        for mat_slot in [m for m in obj.material_slots if ('KK ' in m.name and 'Outline ' not in m.name and ' Outline' not in m.name)]:
            material = mat_slot.material
            if bpy.data.materials.get(material.name + '-ORG'):
                atlas_material = bpy.data.materials.get('{} Atlas'.format(material.name))
                mat_slot.material = atlas_material

    #setup the new collection for exporting
    bpy.data.collections['Collection.001'].name = 'Model with atlas'
    layer_collection = bpy.context.view_layer.layer_collection
    layerColl = recurLayerCollection(layer_collection, 'Model with atlas')
    bpy.context.view_layer.active_layer_collection = layerColl
    bpy.ops.collection.exporter_add(name="IO_FH_fbx")
    bpy.data.collections["Model with atlas"].exporters[0].export_properties.object_types = {'EMPTY', 'ARMATURE', 'MESH', 'OTHER'}
    bpy.data.collections["Model with atlas"].exporters[0].export_properties.use_mesh_modifiers = False
    bpy.data.collections["Model with atlas"].exporters[0].export_properties.add_leaf_bones = False
    bpy.data.collections["Model with atlas"].exporters[0].export_properties.bake_anim = False
    bpy.data.collections["Model with atlas"].exporters[0].export_properties.apply_scale_options = 'FBX_SCALE_ALL'
    bpy.data.collections["Model with atlas"].exporters[0].export_properties.path_mode = 'COPY'
    bpy.data.collections["Model with atlas"].exporters[0].export_properties.embed_textures = False
    bpy.data.collections["Model with atlas"].exporters[0].export_properties.mesh_smooth_type = 'OFF'
    bpy.data.collections["Model with atlas"].exporters[0].export_properties.filepath = os.path.join(folderpath.replace('baked_files', 'atlas_files'), 'Exported model.fbx')

    #hide the new collection
    layerColl = recurLayerCollection(layer_collection, 'Scene Collection')
    bpy.context.view_layer.active_layer_collection = layerColl
    bpy.context.scene.view_layers[0].active_layer_collection.children[0].exclude = False
    bpy.context.scene.view_layers[0].active_layer_collection.children[-1].exclude = True
    #revert the original material's images or they will still be using the resized images for the new uv positions
    remove_orphan_data()

class bake_materials(bpy.types.Operator):
    bl_idname = "kkbp.bakematerials"
    bl_label = "Bake and generate atlased model"
    bl_description = t('bake_mats_tt')
    bl_options = {'REGISTER', 'UNDO'}
        
    def execute(self, context):
        try:
            #just use the pmx folder for the baked files
            scene = context.scene.kkbp
            folderpath = os.path.join(context.scene.kkbp.import_dir, 'baked_files', '')
            last_step = time.time()
            c.toggle_console()
            c.reset_timer()
            c.kklog('Switching to EEVEE for material baking...')
            bpy.context.scene.render.engine = 'BLENDER_EEVEE_NEXT' if bpy.app.version[0] > 3 else 'BLENDER_EEVEE'
            try:
                bpy.ops.object.mode_set(mode='OBJECT')
            except:
                #no active object error
                c.switch(bpy.data.objects['Body'], 'OBJECT')

            #set viewport shading to solid for better performance
            my_areas = bpy.context.workspace.screens[0].areas
            my_shading = 'SOLID'  # 'WIREFRAME' 'SOLID' 'MATERIAL' 'RENDERED'
            for area in my_areas:
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        space.shading.type = my_shading
            #reset LBS node group to "Rim: None" if used
            for mat in bpy.data.materials:
                if mat.node_tree:
                    if mat.node_tree.nodes.get('Rim') and mat.node_tree.nodes.get('LBS'):
                        if mat.node_tree.nodes['Rim'].node_tree == bpy.data.node_groups['LBS']:
                            mat.node_tree.nodes['Rim'].node_tree = bpy.data.node_groups['Rim: None']
                            links = mat.node_tree.links
                            links.new(mat.node_tree.nodes['Shader'].outputs[0], mat.node_tree.nodes['Rim'].inputs[0]) #connect color out to rim input

            resolutionMultiplier = scene.bake_mult
            for ob in [obj for obj in bpy.context.view_layer.objects if obj.type == 'MESH']:
                camera = setup_camera()
                if camera == None:
                    return {'FINISHED'}
                for obj in [obj for obj in bpy.context.view_layer.objects if obj != ob]:
                    obj.hide_render = True
                bpy.ops.object.select_all(action='DESELECT')
                bpy.context.view_layer.objects.active = ob
                ob.select_set(True)
                setup_geometry_nodes_and_fillerplane(camera)
                bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
                #remove the object itself for the old baking system
                if bpy.context.scene.kkbp.old_bake_bool:
                    ob.hide_render = True
                    ob.hide_viewport = True
                start_baking(folderpath, resolutionMultiplier, scene.bake_light_bool, scene.bake_dark_bool, scene.bake_norm_bool)
                for obj in bpy.context.view_layer.objects:
                    obj.hide_render = False
                    ob.hide_viewport = False
                cleanup()
            replace_all_baked_materials(folderpath)
            if scene.use_atlas:
                create_material_atlas(folderpath)
            
            #setup the original collection for exporting
            # https://blender.stackexchange.com/questions/127403/change-active-collection
            #Recursively transverse layer_collection for a particular name
            def recurLayerCollection(layerColl, collName):
                found = None
                if (layerColl.name == collName):
                    return layerColl
                for layer in layerColl.children:
                    found = recurLayerCollection(layer, collName)
                    if found:
                        return found

            layer_collection = bpy.context.view_layer.layer_collection
            layerColl = recurLayerCollection(layer_collection, 'Collection')
            bpy.context.view_layer.active_layer_collection = layerColl
            if bpy.app.version[0] != 3:
                if not bpy.data.collections["Collection"].exporters:
                    bpy.ops.collection.exporter_add(name="IO_FH_fbx")
                    bpy.data.collections["Collection"].exporters[0].export_properties.object_types = {'EMPTY', 'ARMATURE', 'MESH', 'OTHER'}
                    bpy.data.collections["Collection"].exporters[0].export_properties.use_mesh_modifiers = False
                    bpy.data.collections["Collection"].exporters[0].export_properties.add_leaf_bones = False
                    bpy.data.collections["Collection"].exporters[0].export_properties.bake_anim = False
                    bpy.data.collections["Collection"].exporters[0].export_properties.apply_scale_options = 'FBX_SCALE_ALL'
                    bpy.data.collections["Collection"].exporters[0].export_properties.path_mode = 'COPY'
                    bpy.data.collections["Collection"].exporters[0].export_properties.embed_textures = False
                    bpy.data.collections["Collection"].exporters[0].export_properties.mesh_smooth_type = 'OFF'
                    bpy.data.collections["Collection"].exporters[0].export_properties.filepath = os.path.join(folderpath.replace('baked_files', 'atlas_files'), 'Exported model.fbx')
            c.toggle_console()

            c.kklog('Finished in ' + str(time.time() - last_step)[0:4] + 's')
            #reset viewport shading back to material preview
            my_areas = bpy.context.workspace.screens[0].areas
            my_shading = 'SOLID'  # 'WIREFRAME' 'SOLID' 'MATERIAL' 'RENDERED'
            for area in my_areas:
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        space.shading.type = my_shading 
            return {'FINISHED'}
        except:
            c.kklog('Unknown python error occurred', type = 'error')
            c.kklog(traceback.format_exc())
            #reset viewport shading back to solid
            my_areas = bpy.context.workspace.screens[0].areas
            my_shading = 'SOLID'  # 'WIREFRAME' 'SOLID' 'MATERIAL' 'RENDERED'
            for area in my_areas:
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        space.shading.type = my_shading 
            self.report({'ERROR'}, traceback.format_exc())
            return {"CANCELLED"}

if __name__ == "__main__":
    bpy.utils.register_class(bake_materials)

    # test call
    print((bpy.ops.kkbp.bakematerials('INVOKE_DEFAULT')))
