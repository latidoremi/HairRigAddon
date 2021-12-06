# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
    "name": "Hair Rig Addon",
    "author": "Latidoremi",
    "version": (0, 1),
    "blender": (3, 0, 0),
    "location": "Sidebar > Hair Rig",
    "warning": "Experimental",
    "category": "Animation",
}

from . import hair_rig

def register():
    print('Hair Rig registered')
    hair_rig.register()

def unregister():
    print('Hair Rig unregistered')
    hair_rig.unregister()

if __name__ == "__main__":
    register()
