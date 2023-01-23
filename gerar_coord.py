from qgis.core import *

layer = iface.activeLayer()
features = layer.getFeatures()
layer.startEditing()
for feature in features:
    geometry = feature.geometry()
    point = geometry.asPoint()
    feature['coord_x'] = point.x()
    feature['coord_y'] = point.y()
    layer.updateFeature(feature)
    
layer.commitChanges()
