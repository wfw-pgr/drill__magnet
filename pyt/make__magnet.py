import numpy as np
import os, sys
import gmsh

# ========================================================= #
# ===  make__magnet routine                             === #
# ========================================================= #
def make__magnet():

    configFile = "dat/parameter.conf"
    import nkUtilities.load__constants as lcn
    const = lcn.load__constants( inpFile=configFile )
    
    # ------------------------------------------------- #
    # --- [1] initialization of the gmsh            --- #
    # ------------------------------------------------- #
    gmsh.initialize()
    gmsh.option.setNumber( "General.Terminal", 1 )
    gmsh.model.add( "model" )
    
    # ------------------------------------------------- #
    # --- [2] Modeling                              --- #
    # ------------------------------------------------- #
    make_model = True
    if ( make_model ):
        side = "+"
        import generate__magnetParts as mag
        mag.generate__magnetParts( side=side )
    else:
        stpFile = "msh/model.step"
        gmsh.model.occ.importShapes( stpFile )

    import define__ports as dfp
    inpFile = "dat/ports.conf"
    tools   = dfp.define__ports( inpFile=inpFile )
    tools   = [ (3,tool) for tool in tools ]
    gmsh.model.occ.synchronize()
    targets = [ (3,int(target)) for target in const["cut__target"] ]
    gmsh.model.occ.cut( targets, tools, removeObject=False, removeTool=True )
    gmsh.model.occ.synchronize()

    gmsh.model.occ.synchronize()
    gmsh.model.occ.removeAllDuplicates()
    gmsh.model.occ.synchronize()

    # ------------------------------------------------- #
    # --- [3] Mesh settings                         --- #
    # ------------------------------------------------- #
    #  -- [3-1] load and assign mesh.conf           --  # 
    meshFile = "dat/mesh.conf"
    import nkGmshRoutines.assign__meshsize as ams
    meshes = ams.assign__meshsize( meshFile=meshFile )
    gmsh.option.setNumber( "Mesh.CharacteristicLengthMin", np.min( meshes["meshsize_list"] ) )
    gmsh.option.setNumber( "Mesh.CharacteristicLengthMax", np.max( meshes["meshsize_list"] ) )
    #  -- [3-2] set mesh configuration              --  # 
    gmsh.option.setNumber( "Mesh.Algorithm"  , const["mesh__algorithm2D"] )
    gmsh.option.setNumber( "Mesh.Algorithm3D", const["mesh__algorithm3D"] )
    if ( const["mesh__hexa_subdivision"] ):
        gmsh.option.setNumber( "Mesh.SubdivisionAlgorithm", 2 )
    else:
        gmsh.option.setNumber( "Mesh.SubdivisionAlgorithm", 1 )

    # ------------------------------------------------- #
    # --- [4] post process                          --- #
    # ------------------------------------------------- #
    #  -- [4-1] msh model geometry output           --  #
    if ( const["mesh__stepoutput"] ):
        gmsh.write( "msh/model.step" )
    #  -- [4-2] meshing                             --  #
    gmsh.model.occ.synchronize()
    gmsh.model.mesh.generate(3)
    #  -- [4-3] optimization                        --  #
    if ( const["mesh__optimize"] ):
        gmsh.option.setNumber( "Mesh.Optimize", 1 )
        gmsh.model.mesh.optimize( "Netgen" )
        gmsh.model.mesh.optimize( "Relocate3D" )
    #  -- [4-4] save mesh                           --  #
    gmsh.write( "msh/model.msh" )
    if ( const["mesh__bdfoutput"] ):
        gmsh.option.setNumber( "Mesh.BdfFieldFormat"    , 0 )
        gmsh.option.setNumber( "Mesh.SaveElementTagType", 2 )
        gmsh.write( "msh/model.bdf" )
    #  -- [4-5] end                                 --  #
    gmsh.finalize()

    
# ========================================================= #
# ===   実行部                                          === #
# ========================================================= #
if ( __name__=="__main__" ):
    make__magnet()
