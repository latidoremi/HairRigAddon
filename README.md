# HairRigAddon

This addon is inspired by the character rig file from the Blender open source movie Sprit Fright.

In the original file, hair particles are rigged using a script. Since scripting isn't for most Blender users, I make this addon to help artists to animate hair particles more easily without scripting.


# Tutorial

This addon works pretty much the same way as the original script does, the program will constantly move the hair keys to match the target mesh vertex positions by indices, so that any deformation made on the target mesh, the hair particles will follow.

Install the .py file like any other addons

<img src="https://github.com/latidoremi/private_repo/blob/main/hr01.png" width = "247" height = "272" alt="" align=center />

You will see the Hair Rig tab in the N panel

<img src="https://github.com/latidoremi/private_repo/blob/main/hr03.png" width = "389" height = "316" alt="" align=center />

Select any object that has hair particle modifier, a uilist will show up

<img src="https://github.com/latidoremi/private_repo/blob/main/hr04.png" width = "432" height = "356" alt="" align=center />

Hit the add button to add a hair rig layer

A hair rig layer is a custom property store in each object, each layer stores 3 properties:

- **update:** an on/off switch of the update state of the layer
- **particle system:** name of the particle system that you want to control by the target
- **target object:** a pointer to the target object that you want to use to control the hair particles

You can either create target mesh from hair, or create hair from target mesh



## Example 01: Create target mesh from hair

<img src="https://github.com/latidoremi/private_repo/blob/main/hr05.png" width = "443" height = "309" alt="" align=center />

Comb the hair any shape you like, you can change hair keys as well, hair keys doesn't have to be uniform

<img src="https://github.com/latidoremi/private_repo/blob/main/hr06.png" width = "544" height = "330" alt="" align=center />

Select a target object, target object has to be 'MESH' type, in this example I select a cube. Go to the **Target Mesh Specials** menu, hit the **Hair to Mesh** button

<img src="https://github.com/latidoremi/private_repo/blob/main/hr07.png" width = "452" height = "322" alt="" align=center />

Now the target mesh is generated

<img src="https://github.com/latidoremi/private_repo/blob/main/hr08.png" width = "609" height = "322" alt="" align=center />

Add a Simple Deform modifier

<img src="https://github.com/latidoremi/private_repo/blob/main/hr09.png" width = "388" height = "322" alt="" align=center />

Turn on layer update and global update, now the hair particles follow the deformation


## Example 02: Create hair from target mesh

Rules for the target mesh:
- Target mesh must contain only mesh lines (vertices, edges, no faces)
- No branches (no vertex links to more than 2 edges)
- No single vertex (no vertex links to 0 edges)

<img src="https://github.com/latidoremi/private_repo/blob/main/hr10.png" width = "174" height = "307" alt="" align=center />

In this example I make a braid mesh.

<img src="https://github.com/latidoremi/private_repo/blob/main/hr12.png" width = "442" height = "290" alt="" align=center />

Go to the **Target Mesh Specials** menu, hit the **Mesh to Hair** button

Note that each hair particle(strand) has it's own direction like curves, in this operater, end vertex(vertex links to only 1 edge) with a lower index number of a single mesh line defines the root to generate hair from, the order of the rest of the vertices of the same mesh line does not affect the result. Use the measureit addon that comes with blender to visulize the vertex index.

<img src="https://github.com/latidoremi/private_repo/blob/main/mesh_to_hair.png" width = "354" height = "343" alt="" align=center />
<img src="https://github.com/latidoremi/private_repo/blob/main/hr11.png" width = "354" height = "343" alt="" align=center />

One way to make sure that the vertex order is right is to convert the target mesh to curve, go to curve edit mode, turn on draw normals in viewport overlays, you can see if the curves are pointing in the right direction (in most cases should be pointing away from the particle emitter), if not, switch curve direction, once the checking is done, convert back to mesh.

Even though it's ok to generate hair with messy vertex order, the function that moves the particles does not accept messy vertex order!(it is possible to allow messy vertex order using mapping list but it's not performance efficient) So, if you are going to use the same mesh to later control the hair particles, hit the **Hair to Mesh** button along

<img src="https://github.com/latidoremi/private_repo/blob/main/hr13.png" width = "442" height = "290" alt="" align=center />

Now the hair is generated

<img src="https://github.com/latidoremi/private_repo/blob/main/hr14.png" width = "442" height = "290" alt="" align=center />

Tweak some settings if you like

Bind the target mesh to an armature






