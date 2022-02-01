# HairRigAddon

This addon is inspired by the character rig file from the Blender open source movie *Sprit Fright*.

In the original file, hair particles are rigged using a script. Since scripting isn't for most Blender users, I make this addon to help artists to animate hair particles more easily without scripting.


# Tutorial

This addon works pretty much the same way as the original script does, a handler function will constantly set the hair key locations with the target mesh vertex locations by indices, so that any deformation made on the target mesh, the hair particles will follow.

Install the .zip file like any other addons

<img src="https://github.com/latidoremi/hair_rig_readme_images/blob/main/hr01.png" width = "247" height = "272" alt="" align=center />

You will see the Hair Rig tab in the N panel

<img src="https://github.com/latidoremi/hair_rig_readme_images/blob/main/hr03.png" width = "389" height = "316" alt="" align=center />

Select any object that has hair particle modifier, a uilist will show up

<img src="https://github.com/latidoremi/hair_rig_readme_images/blob/main/hr04.png" width = "432" height = "356" alt="" align=center />

Hit the add button to add a hair rig layer

A hair rig layer is a custom property stored in each object, each layer stores 3 sub-properties:

- **update:** an on/off switch of the layer update state
- **particle system:** name of the particle system that you want to control by the target
- **target object:** a pointer to the target object that you want to use to control the hair particles

You can either create target mesh from hair, or create hair from target mesh



## Example 01: Create target mesh from hair

<img src="https://github.com/latidoremi/hair_rig_readme_images/blob/main/hr05.png" width = "443" height = "309" alt="" align=center />

Comb the hair any shape you like, you can change hair keys as well, hair keys doesn't have to be uniform

<img src="https://github.com/latidoremi/hair_rig_readme_images/blob/main/hr06.png" width = "454" height = "290" alt="" align=center />

Select a target object, target object has to be 'MESH' type, in this example I select a cube. Go to the **Target Mesh Specials** menu, hit the **Hair to Mesh** button

<img src="https://github.com/latidoremi/hair_rig_readme_images/blob/main/hr07.png" width = "452" height = "322" alt="" align=center />

Now the target mesh is generated

<img src="https://github.com/latidoremi/hair_rig_readme_images/blob/main/hr08.png" width = "609" height = "322" alt="" align=center />

Add a Simple Deform modifier

<img src="https://github.com/latidoremi/hair_rig_readme_images/blob/main/hr09.png" width = "388" height = "322" alt="" align=center />

Turn on layer update and global update, now the hair particles follow the deformation


## Example 02: Create hair from target mesh

Rules for the target mesh:
- Target mesh must contain only mesh lines (vertices, edges, no faces)
- No branches (no vertex links to more than 2 edges)
- No single vertex (no vertex links to 0 edges)

<img src="https://github.com/latidoremi/hair_rig_readme_images/blob/main/hr10.png" width = "174" height = "307" alt="" align=center />

In this example I make a braid mesh.

<img src="https://github.com/latidoremi/hair_rig_readme_images/blob/main/hr12.png" width = "450" height = "271" alt="" align=center />

Go to the **Target Mesh Specials** menu, hit the **Mesh to Hair** button

Note that this operator does allow random vertex order, but there's one limitation.

<img src="https://github.com/latidoremi/hair_rig_readme_images/blob/main/mesh_to_hair.png" width = "279" height = "271" alt="" align=center />

Each hair particle(strand) has it's own direction like curves, in each strand, end vertex(vertex links to only 1 edge，each strand has two ends) with a lower index number defines the root to generate hair from, the order of the rest of the vertices does not affect the result. However if the root vertex is wrong, the hair will flip (sorry currently I can't think of a better way to find root vertex...)

Use the measureit addon that comes with blender to visualize vertex indices.

<img src="https://github.com/latidoremi/hair_rig_readme_images/blob/main/hr11.png" width = "354" height = "343" alt="" align=center />

One way to make sure that the vertex order is right is to convert the target mesh to curve, go to curve edit mode, turn on draw normals under viewport overlays, you can see if the curves are pointing in the right direction (in most cases should be pointing away from the particle emitter), if not, switch curve direction, and convert back to mesh.

<img src="https://github.com/latidoremi/hair_rig_readme_images/blob/main/hr13.png" width = "381" height = "343" alt="" align=center />

Now the hair is generated

<img src="https://github.com/latidoremi/hair_rig_readme_images/blob/main/hr14.png" width = "555" height = "360" alt="" align=center />

Tweak some settings if you like

<img src="https://github.com/latidoremi/hair_rig_readme_images/blob/main/hr15.png" width = "508" height = "274" alt="" align=center />

Bind the target mesh to an armature with automatic weights

<img src="https://github.com/latidoremi/hair_rig_readme_images/blob/main/hr16.png" width = "432" height = "274" alt="" align=center />

Turn on layer update and global update, now you can use armature to control hair particles


## Link to other files

Hair rig layer data are stored in Object level and will not lose when objects being linked to other files, but the hair rig object list is stored in Scene level, this list will be read by the handler function, so even an object has hair rig layer data, if it is not in the list, hair particles will not update, this design is mainly for performance efficiency. To recalculate the list, simply press the **Initialize** button right beside the **Global Update** switch, and you're good to go.
