# System modules.
from imp import reload

# Maya modules.
import maya.cmds as mc

# ncscript modules.
from ncTools.rig import core
reload(core)


class AimConstraint(core.Node):
    def __init__(self, name = 'aimConstraint', **kwargs):
        node = mc.createNode('aimConstraint', n = name, **kwargs)
        super(AimConstraint, self).__init__(node)

class AddDoubleLinear(core.Node):
    def __init__(self, name = 'addDoubleLinear', **kwargs):
        node = mc.createNode('addDoubleLinear', n = name, **kwargs)
        super(AddDoubleLinear, self).__init__(node)

class AngleBetween(core.Node):
    def __init__(self, name = 'angleBetween', **kwargs):
        node = mc.createNode('angleBetween', n = name, **kwargs)
        super(AngleBetween, self).__init__(node)

class AnimCurveTU(core.Node):
    def __init__(self, name = 'animCurveTU', **kwargs):
        node = mc.createNode('animCurveTU', n = name, **kwargs)
        super(AnimCurveTU, self).__init__(node)

class BlendTwoAttr(core.Node):
    def __init__(self, name = 'blendTwoAttr', **kwargs):
        node = mc.createNode('blendTwoAttr', n = name, **kwargs)
        super(BlendTwoAttr, self).__init__(node)

class BlendColors(core.Node):
    def __init__(self, name = 'blendColors', **kwargs):
        node = mc.createNode('blendColors', n = name, **kwargs)
        super(BlendColors, self).__init__(node)

class Clamp(core.Node):
    def __init__(self, name = 'clamp', **kwargs):
        node = mc.createNode('clamp', n = name, **kwargs)
        super(Clamp, self).__init__(node)

class Condition(core.Node):
    def __init__(self, name = 'condition', **kwargs):
        node = mc.createNode('condition', n = name, **kwargs)
        super(Condition, self).__init__(node)

class CurveInfo(core.Node):
    def __init__(self, name = 'curveInfo', **kwargs):
        node = mc.createNode('curveInfo', n = name, **kwargs)
        super(CurveInfo, self).__init__(node)

class CurveFromMeshEdge(core.Node):
    def __init__(self, name = 'curveFromMeshEdge', **kwargs):
        node = mc.createNode('curveFromMeshEdge', n = name, **kwargs)
        super(CurveFromMeshEdge, self).__init__(node)

class CurveFromSurfaceIso(core.Node):
    def __init__(self, name = 'curveFromSurfaceIso', **kwargs):
        node = mc.createNode('curveFromSurfaceIso', n = name, **kwargs)
        super(CurveFromSurfaceIso, self).__init__(node)

class ClosestPointOnMesh(core.Node):
    def __init__(self, name = 'closestPointOnMesh', **kwargs):
        node = mc.createNode('closestPointOnMesh', n = name, **kwargs)
        super(ClosestPointOnMesh, self).__init__(node)

class ClosestPointOnSurface(core.Node):
    def __init__(self, name = 'closestPointOnSurface', **kwargs):
        node = mc.createNode('closestPointOnSurface', n = name, **kwargs)
        super(ClosestPointOnSurface, self).__init__(node)

class DecomposeMatrix(core.Node):
    def __init__(self, name = 'decomposeMatrix', **kwargs):
        node = mc.createNode('decomposeMatrix', n = name, **kwargs)
        super(DecomposeMatrix, self).__init__(node)

class DistanceBetween(core.Node):
    def __init__(self, name = 'distanceBetween', **kwargs):
        node = mc.createNode('distanceBetween', n = name, **kwargs)
        super(DistanceBetween, self).__init__(node)

class Follicle(core.Dag):
    def __init__(self, name = 'follicle', nurbSurface = '', **kwargs):
        node = mc.createNode('follicle', n = name, **kwargs)
        super(Follicle, self).__init__(node)

        node_parent = self.get_parent()
        self.attr('outRotate') >> node_parent.attr('rotate')
        self.attr('outTranslate') >> node_parent.attr('translate')

        if nurbSurface:
            nrb = core.Dag(nurbSurface)
            nrb.shape.attr('local') >> self.attr('inputSurface')
            nrb.shape.attr('worldMatrix') >> self.attr('inputWorldMatrix')

class Transform(core.Dag):
    def __init__(self, name = 'transform', **kwargs):
        node = mc.createNode('transform', n = name, **kwargs)
        super(Transform, self).__init__(node)

class Joint(core.Dag):
    def __init__(self, name = 'joint', **kwargs):
        node = mc.createNode('joint', n = name)
        super(Joint, self).__init__(node)
        if 'position' in kwargs:
            self.snap_matrix(kwargs['position'])
            self.freeze()

class HairSystem(core.Node):
    def __init__(self, name = 'hairSystem', **kwargs):
        node = mc.createNode('hairSystem', n = name, **kwargs)
        super(HairSystem, self).__init__(node)
        
class Loft(core.Node):
    def __init__(self, name = 'loft', **kwargs):
        node = mc.createNode('loft', n = name, **kwargs)
        super(Loft, self).__init__(node)

class Locator(core.Dag):
    def __init__(self, name = 'locator', **kwargs):
        node = mc.createNode('locator', n = name, **kwargs)
        super(Locator, self).__init__(node)

class MultiplyDivide(core.Node):
    def __init__(self, name = 'multiplyDivide', **kwargs):
        node = mc.createNode('multiplyDivide', n = name, **kwargs)
        super(MultiplyDivide, self).__init__(node)

class MultDoubleLinear(core.Node):
    def __init__(self, name = 'multDoubleLinear', **kwargs):
        node = mc.createNode('multDoubleLinear', n = name, **kwargs)
        super(MultDoubleLinear, self).__init__(node)

class MultMatrix(core.Node):
    def __init__(self, name = 'multMatrix', **kwargs):
        node = mc.createNode('multMatrix', n = name, **kwargs)
        super(MultMatrix, self).__init__(node)
        self.add_attr('localOffset', at = 'fltMatrix')
        self.attr('localOffset') >> self.attr('matrixIn[0]')

class Nucleus(core.Node):
    def __init__(self, name = 'nucleus', **kwargs):
        node = mc.createNode('nucleus', n = name, **kwargs)
        super(Nucleus, self).__init__(node)

class NearestPointOnCurve(core.Node):
    def __init__(self, name = 'nearestPointOnCurve', **kwargs):
        node = mc.createNode('nearestPointOnCurve', n = name, **kwargs)
        super(NearestPointOnCurve, self).__init__(node)

class NurbsCurve(core.Node):
    def __init__(self, name = 'nurbsCurve', **kwargs):
        node = mc.createNode('nurbsCurve', n = name, **kwargs)
        super(NurbsCurve, self).__init__(node)

class PairBlend(core.Node):
    def __init__(self, name = 'pairBlend', **kwargs):
        node = mc.createNode('pairBlend', n = name, **kwargs)
        super(PairBlend, self).__init__(node)

class PlusMinusAverage(core.Node):
    def __init__(self, name = 'plusMinusAverage', **kwargs):
        node = mc.createNode('plusMinusAverage', n = name, **kwargs)
        super(PlusMinusAverage, self).__init__(node)

class PointOnCurveInfo(core.Node):
    def __init__(self, name = 'pointOnCurveInfo', **kwargs):
        node = mc.createNode('pointOnCurveInfo', n = name, **kwargs)
        super(PointOnCurveInfo, self).__init__(node)

class PointOnSurfaceInfo(core.Node):
    def __init__(self, name = 'pointOnSurfaceInfo', **kwargs):
        node = mc.createNode('pointOnSurfaceInfo', n = name, **kwargs)
        super(PointOnSurfaceInfo, self).__init__(node)

class RebuildCurve(core.Node):
    def __init__(self, name = 'rebuildCurve', **kwargs):
        node = mc.createNode('rebuildCurve', n = name, **kwargs)
        super(RebuildCurve, self).__init__(node)

class RemapValue(core.Node):
    def __init__(self, name = 'remapValue', **kwargs):
        node = mc.createNode('remapValue', n = name, **kwargs)
        super(RemapValue, self).__init__(node)

class Reverse(core.Node):
    def __init__(self, name = 'reverse', **kwargs):
        node = mc.createNode('reverse', n = name, **kwargs)
        super(Reverse, self).__init__(node)

class UvPin(core.Node):
    def __init__(self, name = 'unPin', **kwargs):
        node = mc.createNode('unPin', n = name, **kwargs)
        super(UvPin, self).__init__(node)
        
class AimMatrix(core.Node):
    def __init__(self, name = 'aimMatrix', **kwargs):
        node = mc.createNode('aimMatrix', n = name, **kwargs)
        super(AimMatrix, self).__init__(node)
        
class ComposeMatrix(core.Node):
    def __init__(self, name = 'composeMatrix', **kwargs):
        node = mc.createNode('composeMatrix', n = name, **kwargs)
        super(ComposeMatrix, self).__init__(node)
        
class WtAddMatrix(core.Node):
    def __init__(self, name = 'wtAddMatrix', **kwargs):
        node = mc.createNode('wtAddMatrix', n = name, **kwargs)
        super(WtAddMatrix, self).__init__(node)
        
class FourByFourMatrix(core.Node):
    def __init__(self, name = 'fourByFourMatrix', **kwargs):
        node = mc.createNode('fourByFourMatrix', n = name, **kwargs)
        super(FourByFourMatrix, self).__init__(node)
        
class InverseMatrix(core.Node):
    def __init__(self, name = 'inverseMatrix', **kwargs):
        node = mc.createNode('inverseMatrix', n = name, **kwargs)
        super(InverseMatrix, self).__init__(node)
        
class QuatToEuler(core.Node):
    def __init__(self, name = 'quatToEuler', **kwargs):
        node = mc.createNode('quatToEuler', n = name, **kwargs)
        super(QuatToEuler, self).__init__(node)
        
class EulerToQuat(core.Node):
    def __init__(self, name = 'eulerToQuat', **kwargs):
        node = mc.createNode('eulerToQuat', n = name, **kwargs)
        super(EulerToQuat, self).__init__(node)
        
class QuatProd(core.Node):
    def __init__(self, name = 'quatProd', **kwargs):
        node = mc.createNode('quatProd', n = name, **kwargs)
        super(QuatProd, self).__init__(node)
        
class QuatInvert(core.Node):
    def __init__(self, name = 'quatInvert', **kwargs):
        node = mc.createNode('quatInvert', n = name, **kwargs)
        super(QuatInvert, self).__init__(node)
        
class QuatAdd(core.Node):
    def __init__(self, name = 'quatAdd', **kwargs):
        node = mc.createNode('quatAdd', n = name, **kwargs)
        super(QuatAdd, self).__init__(node)
        
class QuatSub(core.Node):
    def __init__(self, name = 'quatSub', **kwargs):
        node = mc.createNode('quatSub', n = name, **kwargs)
        super(QuatSub, self).__init__(node)
        
class QuatSlerp(core.Node):
    def __init__(self, name = 'quatSlerp', **kwargs):
        node = mc.createNode('quatSlerp', n = name, **kwargs)
        super(QuatSlerp, self).__init__(node)
        
class QuatNormalize(core.Node):
    def __init__(self, name = 'quatNormalize', **kwargs):
        node = mc.createNode('quatNormalize', n = name, **kwargs)
        super(QuatNormalize, self).__init__(node)
        
class QuatToAxisAngle(core.Node):
    def __init__(self, name = 'quatToAxisAngle', **kwargs):
        node = mc.createNode('quatToAxisAngle', n = name, **kwargs)
        super(QuatToAxisAngle, self).__init__(node)
        
class QuatConjugate(core.Node):
    def __init__(self, name = 'quatConjugate', **kwargs):
        node = mc.createNode('quatConjugate', n = name, **kwargs)
        super(QuatConjugate, self).__init__(node)
        
class VectorProduct(core.Node):
    def __init__(self, name = 'vectorProduct', **kwargs):
        node = mc.createNode('vectorProduct', n = name, **kwargs)
        super(VectorProduct, self).__init__(node)