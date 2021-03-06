'''
IMPORT KK TEMPLATES SCRIPT
- Appends the material templates from the KK Shader .blend file
Usage:
- Click the button and choose the KK shader .blend file
'''

import bpy
import os

from bpy.props import StringProperty, BoolProperty
from bpy_extras.io_utils import ImportHelper
from bpy.types import Operator

class import_Templates(Operator, ImportHelper):
    bl_idname = "kkb.importtemplates"
    bl_label = "Open KK Shader .blend"
    bl_description = "Open the KK Shader .blend file"
    bl_options = {'REGISTER', 'UNDO'}
    
    filter_glob: StringProperty(
        default='*.blend',
        options={'HIDDEN'}
    )
    
    def execute(self, context):

        #Clean material list
        armature = bpy.data.objects['Armature']
        armature.hide = False
        bpy.context.view_layer.objects.active = None
        bpy.ops.object.select_all(action='DESELECT')
        for ob in bpy.context.view_layer.objects:
            if ob.type == 'MESH':
                ob.select_set(True)
                bpy.context.view_layer.objects.active = ob
        
        armature.hide = True
        bpy.ops.object.material_slot_remove_unused()
        
        #import all material templates
        filepath = self.filepath
        innerpath = 'Material'
        templateList = ['Template Body', 'Template Outline', 'Template Body Outline', 'Template Eye (hitomi)', 'Template Eyebrows (mayuge)', 'Template Eyeline down', 'Template Eyeline up', 'Template Eyewhites (sirome)', 'Template Face', 'Template General', 'Template Hair', 'Template Mixed Metal or Shiny', 'Template Nose', 'Template Shadowcast (Standard)', 'Template Teeth (tooth)']

        for template in templateList:
            bpy.ops.wm.append(
                filepath=os.path.join(filepath, innerpath, template),
                directory=os.path.join(filepath, innerpath),
                filename=template,
                #set_fake=True
                )
        
        #Replace all materials on the body with templates
        body = bpy.data.objects['Body']
        def bodySwap(original, template):
            try:
                body.material_slots[original].material = bpy.data.materials[template]
            except:
                print('material or template wasn\'t found: ' + original + ' / ' + template)

        bodySwap('cf_m_face_00','Template Face')
        bodySwap('cf_m_mayuge_00','Template Eyebrows (mayuge)')
        bodySwap('cf_m_noseline_00','Template Nose')
        bodySwap('cf_m_eyeline_00_up','Template Eyeline up')
        bodySwap('cf_m_eyeline_down','Template Eyeline down')
        bodySwap('cf_m_sirome_00','Template Eyewhites (sirome)')
        bodySwap('cf_m_sirome_00.001','Template Eyewhites (sirome)')
        bodySwap('cf_m_hitomi_00','Template Eye (hitomi)')
        bodySwap('cf_m_hitomi_00.001','Template Eye (hitomi)')
        bodySwap('cf_m_body','Template Body')
        bodySwap('cf_m_tooth','Template Teeth (tooth)')
        bodySwap('cf_m_tang','Template General')
        
        #Make the tongue material unique so parts of the General Template aren't overwritten
        
        tongueTemplate = bpy.data.materials['Template General'].copy()
        tongueTemplate.name = 'Template Tongue'
        body.material_slots['Template General'].material = tongueTemplate
        
        #Make the texture group unique
        newNode = tongueTemplate.node_tree.nodes['Gentex'].node_tree.copy()
        tongueTemplate.node_tree.nodes['Gentex'].node_tree = newNode
        newNode.name = 'Tongue Textures'
        
        #Make the shader group unique
        newNode = tongueTemplate.node_tree.nodes['KKShader'].node_tree.copy()
        tongueTemplate.node_tree.nodes['KKShader'].node_tree = newNode
        newNode.name = 'Tongue Shader'
        
        #Replace all of the Hair materials with hair templates and name accordingly
        hair = bpy.data.objects['Hair']
        for original in hair.material_slots:
            template = bpy.data.materials['Template Hair'].copy()
            template.name = 'Template ' + original.name
            original.material = bpy.data.materials[template.name]
        
        #Replace all other materials with the general template and name accordingly
        for ob in bpy.context.view_layer.objects:
            if ob.type == 'MESH' and ('Body' not in ob.name and 'Hair' not in ob.name):
                for original in ob.material_slots:
                    template = bpy.data.materials['Template General'].copy()
                    template.name = 'Template ' + original.name
                    original.material = bpy.data.materials[template.name]
        
        # Get rid of the duplicate node groups cause there's a lot
        #stolen from somwhere
        def eliminate(node):
            node_groups = bpy.data.node_groups

            # Get the node group name as 3-tuple (base, separator, extension)
            (base, sep, ext) = node.node_tree.name.rpartition('.')

            # Replace the numeric duplicate
            if ext.isnumeric():
                if base in node_groups:
                    print("  Replace '%s' with '%s'" % (node.node_tree.name, base))
                    node.node_tree.use_fake_user = False
                    node.node_tree = node_groups.get(base)

        #--- Search for duplicates in actual node groups
        node_groups = bpy.data.node_groups

        for group in node_groups:
            for node in group.nodes:
                if node.type == 'GROUP':
                    eliminate(node)

        #--- Search for duplicates in materials
        mats = list(bpy.data.materials)
        worlds = list(bpy.data.worlds)

        for mat in mats + worlds:
            if mat.use_nodes:
                for node in mat.node_tree.nodes:
                    if node.type == 'GROUP':
                        eliminate(node)

        #Import custom bone shapes
        filepath = self.filepath
        innerpath = 'Collection'
        templateList = ['Bone Widgets']

        for template in templateList:
            bpy.ops.wm.append(
                filepath=os.path.join(filepath, innerpath, template),
                directory=os.path.join(filepath, innerpath),
                filename=template,
                #set_fake=True
                )
        
        #apply custom bone shapes
        #Select the armature and make it active
        bpy.ops.object.select_all(action='DESELECT')
        armature = bpy.data.objects['Armature']
        armature.hide = False
        armature.select_set(True)
        bpy.context.view_layer.objects.active=armature
        
        #Add custom shapes to the armature        
        armature.data.show_bone_custom_shapes = True
        bpy.ops.object.mode_set(mode='POSE')

        bpy.context.object.pose.bones["Hips"].custom_shape = bpy.data.objects["WidgetHips"]
        bpy.context.object.pose.bones["Spine"].custom_shape = bpy.data.objects["WidgetSpine"]
        bpy.context.object.pose.bones["Chest"].custom_shape = bpy.data.objects["WidgetChest"]
        bpy.context.object.pose.bones["Cf_D_Bust00"].custom_shape = bpy.data.objects["WidgetBust"]
        bpy.context.object.pose.bones["Left shoulder"].custom_shape = bpy.data.objects["WidgetShoulder"]
        bpy.context.object.pose.bones["Right shoulder"].custom_shape = bpy.data.objects["WidgetShoulder"]
        bpy.context.object.pose.bones["Cf_Pv_Foot_R"].custom_shape = bpy.data.objects["WidgetFoot"]
        bpy.context.object.pose.bones["Cf_Pv_Foot_L"].custom_shape = bpy.data.objects["WidgetFoot"]
        bpy.context.object.pose.bones["Right toe"].custom_shape = bpy.data.objects["WidgetToe"]
        bpy.context.object.pose.bones["Left toe"].custom_shape = bpy.data.objects["WidgetToe"]
        bpy.context.object.pose.bones["Cf_Pv_Knee_L"].custom_shape = bpy.data.objects["WidgetKnee"]
        bpy.context.object.pose.bones["Cf_Pv_Knee_R"].custom_shape = bpy.data.objects["WidgetKnee"]
        bpy.context.object.pose.bones["Cf_Pv_Elbo_L"].custom_shape = bpy.data.objects["WidgetKnee"]
        bpy.context.object.pose.bones["Cf_Pv_Elbo_R"].custom_shape = bpy.data.objects["WidgetKnee"]
        bpy.context.object.pose.bones["Neck"].custom_shape = bpy.data.objects["WidgetNeck"]
        bpy.context.object.pose.bones["Head"].custom_shape = bpy.data.objects["WidgetHead"]
        bpy.context.object.pose.bones["Cf_Pv_Hand_R"].custom_shape = bpy.data.objects["WidgetHandR"]
        bpy.context.object.pose.bones["Cf_Pv_Hand_L"].custom_shape = bpy.data.objects["WidgetHandL"]
        bpy.context.object.pose.bones["AH1_L"].custom_shape = bpy.data.objects["WidgetBreast"]
        bpy.context.object.pose.bones["AH1_R"].custom_shape = bpy.data.objects["WidgetBreast"]
        bpy.context.object.pose.bones["Eye Controller"].custom_shape = bpy.data.objects["WidgetEye"]

        try:
            bpy.context.space_data.overlay.show_relationship_lines = False
        except:
            #the script was run in the text editor or console, so this won't work
            pass

        #scale all skirt bones
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.armature.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='POSE')

        def resizeBone(bone, scale, type='MIDPOINT'):
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.armature.select_all(action='DESELECT')
            bpy.context.object.data.edit_bones[bone].select_head = True
            bpy.context.object.data.edit_bones[bone].select_tail = True
            if type == 'MIDPOINT':
                bpy.ops.transform.resize(value=(scale, scale, scale), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=0.683013, use_proportional_connected=False, use_proportional_projected=False)
            else:
                bpy.context.object.data.edit_bones[bone].tail=(bpy.context.object.data.edit_bones[bone].tail+bpy.context.object.data.edit_bones[bone].head)/2
                bpy.context.object.data.edit_bones[bone].tail=(bpy.context.object.data.edit_bones[bone].tail+bpy.context.object.data.edit_bones[bone].head)/2
                bpy.context.object.data.edit_bones[bone].tail=(bpy.context.object.data.edit_bones[bone].tail+bpy.context.object.data.edit_bones[bone].head)/2
            bpy.context.object.data.edit_bones[bone].select_head = False
            bpy.context.object.data.edit_bones[bone].select_tail = False
            bpy.ops.object.mode_set(mode='POSE')
        
        skirtbones = [0,1,2,3,4,5,6,7]
        skirtlength = [0,1,2,3,4]

        for root in skirtbones:
            bpy.context.object.pose.bones['Cf_D_Sk_0'+str(root)+'_00'].custom_shape = bpy.data.objects['WidgetSkirt']
            bpy.ops.object.mode_set(mode='EDIT')
            for chain in skirtlength:
                resizeBone('Sk_0'+str(root)+'_0'+str(chain), 0.25)
            bpy.ops.object.mode_set(mode='POSE')
        
        #scale and apply eye bones, mouth bones, eyebrow bones
        bpy.ops.object.mode_set(mode='POSE')
        
        eyebones = [1,2,3,4,5,6,7,8]
        
        for piece in eyebones:
            left = 'Eye0'+str(piece)+'_S_L'
            right = 'Eye0'+str(piece)+'_S_R'
            
            armature.data.bones[left].hide=False
            armature.data.bones[right].hide=False
            bpy.context.object.pose.bones[left].custom_shape  = bpy.data.objects['WidgetFace']
            bpy.context.object.pose.bones[right].custom_shape = bpy.data.objects['WidgetFace']
            
            resizeBone(left, 0.1, 'face')
            resizeBone(right, 0.1, 'face')
        
        restOfFace = ['Mayu_R', 'MayuMid_S_R', 'MayuTip_S_R', 'Mayu_L', 'MayuMid_S_L', 'MayuTip_S_L', 'Mouth_R', 'Mouth_L', 'Mouthup', 'MouthLow', 'MouthMove']
        
        for bone in restOfFace:
            armature.data.bones[bone].hide=False
            bpy.context.object.pose.bones[bone].custom_shape  = bpy.data.objects['WidgetFace']
            resizeBone(bone, 0.1, 'face')
        
        bpy.ops.object.mode_set(mode='POSE')
            
        #hide the extra bones that aren't needed for IK
        nonIK = ['Left elbow', 'Right elbow', 'Left arm', 'Right arm', 'Left leg', 'Right leg', 'Left knee', 'Right knee', 'Right ankle', 'Left ankle']
        for bone in nonIK:
            armature.data.bones[bone].hide = True
        bpy.context.object.data.display_type = 'STICK'
        
        #move eye bone location
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.armature.select_all(action='DESELECT')

        bpy.context.object.data.edit_bones['Eyesx'].head.y = bpy.context.object.data.edit_bones['AH1_R'].tail.y
        bpy.context.object.data.edit_bones['Eyesx'].tail.y = bpy.context.object.data.edit_bones['AH1_R'].tail.y*1.5
        bpy.context.object.data.edit_bones['Eyesx'].tail.z = bpy.context.object.data.edit_bones['N_EyesLookTargetP'].head.z
        bpy.context.object.data.edit_bones['Eyesx'].head.z = bpy.context.object.data.edit_bones['N_EyesLookTargetP'].head.z

        bpy.context.object.data.edit_bones['Eye Controller'].head.y = bpy.context.object.data.edit_bones['AH1_R'].tail.y
        bpy.context.object.data.edit_bones['Eye Controller'].tail.y = bpy.context.object.data.edit_bones['AH1_R'].tail.y*1.5
        bpy.context.object.data.edit_bones['Eye Controller'].tail.z = bpy.context.object.data.edit_bones['N_EyesLookTargetP'].head.z
        bpy.context.object.data.edit_bones['Eye Controller'].head.z = bpy.context.object.data.edit_bones['N_EyesLookTargetP'].head.z
        
        #Add some bones to bone groups
        bpy.ops.object.mode_set(mode='POSE')
        bpy.ops.pose.select_all(action='DESELECT')
        bpy.ops.pose.group_add()
        group = armature.pose.bone_groups['Group']
        group.name = 'IK controllers'
        armature.data.bones['Cf_Pv_Hand_L'].select = True
        armature.data.bones['Cf_Pv_Hand_R'].select = True
        armature.data.bones['Cf_Pv_Foot_R'].select = True
        armature.data.bones['Cf_Pv_Foot_L'].select = True
        bpy.ops.pose.group_assign(type=1)
        group.color_set = 'THEME01'
        
        bpy.ops.pose.select_all(action='DESELECT')
        bpy.ops.pose.group_add()
        group = armature.pose.bone_groups['Group']
        group.name = 'IK poles'
        armature.pose.bone_groups.active_index = 1
        armature.data.bones['Cf_Pv_Elbo_R'].select = True
        armature.data.bones['Cf_Pv_Elbo_L'].select = True
        armature.data.bones['Cf_Pv_Knee_R'].select = True
        armature.data.bones['Cf_Pv_Knee_L'].select = True
        bpy.ops.pose.group_assign(type=1)
        group.color_set = 'THEME09'
        
        bpy.ops.object.mode_set(mode='OBJECT')
        return {'FINISHED'}


if __name__ == "__main__":
    bpy.utils.register_class(import_Templates)

    # test call
    print((bpy.ops.kkb.importtemplates('INVOKE_DEFAULT')))
    
    
