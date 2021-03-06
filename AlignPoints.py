# menuTitle: Align Points
# shortCut: shift+command+f

'''
This script aligns selected points intelligently. 
It will look at the x-coordinate offset and 
the y-coordinate offset and align according to 
whichever one is smaller. It will also make 
an educated guess as to which direction you'd 
like to align it.

Requires Robofont 3.2+

Ryan Bugden
2019.03.09
with thanks to Frank Griesshammer for the idea
'''

def findRange(l):
    # Find the width of the selection and height of the selection independently
    return max(l) - min(l)

def avgList(l):
    # Average the x and y lists independently
    return int(sum(l) / len(l))

def _adjacentPointsThatAreOffCurve(point_index):
    adjacents = [point_index-1, point_index+1]
    l = []
    for pt_i in adjacents:
        # Will avoid errors with first/last point indexes
        try: 
            p.contour._getPoint(pt_i)
        except IndexError:
            continue
        if p.contour.points[pt_i].type == 'offcurve':
            l.append(pt_i)
    return l
     
g = CurrentGlyph()

# Only works if there is a point selection
if g.selection:
    with g.undo("Align Points"):
        x_ind = []
        y_ind = []
        # Parse out the x and y values of the selected glyphs
        for p in g.selection:
            x_ind.append(p.x)
            y_ind.append(p.y)
            
        av_x = avgList(x_ind)
        max_x = max(x_ind)
        min_x = min(x_ind)
        
        av_y = avgList(y_ind)
        max_y = max(y_ind)
        min_y = min(y_ind)
        
        # Threshold to determine whether to move off-curves drastically or not.
        ocp_dist_threshold = 1
        # If the points are closer together horizontally, align x.
        if findRange(x_ind) < findRange(y_ind):
            for p in g.selection: 
                p_i = p._get_index()
                
                # Set appropriate alignment. Tries to intuit whether you want to align left, right, or center.
                if max_x == g.bounds[2]:
                    alignment_x = max_x
                elif min_x == g.bounds[0]:
                    alignment_x = min_x
                else:
                    alignment_x = av_x
                    
                x_delta = alignment_x - p.x
                p.x = alignment_x
                
                # Don't forget off-curves
                for ocp_i in _adjacentPointsThatAreOffCurve(p_i):
                    # If the point is close enough, it will snap to the alignment average.
                    if p.contour.points[p_i].x + ocp_dist_threshold > p.contour.points[ocp_i].x > p.contour.points[p_i].x - ocp_dist_threshold:
                        p.contour.points[ocp_i].x = alignment_x
                    # If it's a smooth point and the handle isn't parallel to the alignment direction, the off-curve will snap to the alignment average.
                    elif p.smooth == True and p.contour.points[ocp_i].y < p.y - ocp_dist_threshold:
                        p.contour.points[ocp_i].x = alignment_x
                    elif p.smooth == True and p.contour.points[ocp_i].y > p.y + ocp_dist_threshold:
                        p.contour.points[ocp_i].x = alignment_x
                    # Otherwise, the off-curve-to-on-curve relationship will be maintained
                    else:
                        p.contour.points[ocp_i].x += x_delta
        # Same for y
        else:
            for p in g.selection:
                p_i = p._get_index()
                
                # Set appropriate alignment. Tries to intuit whether you want to align left, right, or center.
                if max_y == g.bounds[3]:
                    alignment_y = max_y
                elif min_y == g.bounds[1]:
                    alignment_y = min_y
                else:
                    alignment_y = av_y
                   
                y_delta = alignment_y - p.y    
                p.y = alignment_y
                
                # Don't forget off-curves
                for ocp_i in _adjacentPointsThatAreOffCurve(p_i):
                    if p.contour.points[p_i].y + ocp_dist_threshold > p.contour.points[ocp_i].y > p.contour.points[p_i].y - ocp_dist_threshold:
                        p.contour.points[ocp_i].y = alignment_y
                    elif p.smooth == True and p.contour.points[ocp_i].x < p.x - ocp_dist_threshold:
                        p.contour.points[ocp_i].y = alignment_y
                    elif p.smooth == True and p.contour.points[ocp_i].x > p.x + ocp_dist_threshold:
                        p.contour.points[ocp_i].y = alignment_y
                    else:
                        p.contour.points[ocp_i].y += y_delta
                        
        # Immediately reflect the changes in glyph view.
        g.changed()
        
    