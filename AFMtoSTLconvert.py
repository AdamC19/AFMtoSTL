#-------------------------------------------------------------------------------
# Name:        AFMtoSTLconvert
# Purpose:     Converts AFM scans exported as ASCII files to STL files suitable for 3d printing
#
# Author:      Adam Cordingley
#              cordingleya@live.marshall.edu
#              http://acordingley.us
#
# Created:     24/06/2016
# Copyright:   (c) Mike Norton, Adam Cordingley 2016
#
#-------------------------------------------------------------------------------
import copy
import math

#-------------------------------------------------------------------------------
class Vertex:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

#-------------------------------------------------------------------------------
##class Vector:
##    def __init__(self, x, y, z):
##        self.x = x
##        self.y = y
##        self.z = z
##
##    hyp = math.sqrt( x**2 + y** + z** )


#-------------------------------------------------------------------------------

BASE = "C:\\Users\\A_Cordingley\\Desktop\\MBIC\\Adam_MBIC_2016\\summer\\AFM_ASCII\\"
modelName = "test_object"
facetCount = 0
nameIn = ""#"ah-1-20co01-SA-1D-PP-9-16bio-reg_cs2_ASCII.txt"   #"excerpt.txt"
def main():
    done = False
    while not done:
        nameIn = input("ASCII input file name?: ")
        outFileName = input("Output file name (include extension): ")
        try:
            file = open(BASE+nameIn, 'rb')
        except:
            print("File not found. :(")
        try:
            outfile = open(BASE+outFileName, 'w')  #"output2.stl"
        except:
            print("Cannot create file. :(")

        lenX = 0    #int(input("X Length?: "))
        lenY = 0    #int(input("Y Length?: "))
        try:
            baseThickness = float(input("Thickness of base?: "))
        except:
            baseThickness = 1.0
        user = (input("Enter Scan-Size(nm)/samples-per-line: "))
        nums = user.split("/")
        nmPerSample = float(nums[0]) / float(nums[1])
        #nmPerSample = 2500.0/1024.0
        #print(nmPerSample)
        zScale = float(input("Z scale factor?: "))


        #FIND LOWEST POINT
        rawHeights = []
        lowest = 0.0e0
        for line in file:
            try:
                num = float(line.strip())
                rawHeights.append(num)  #make a big array
                if num < lowest:
                    lowest = num
            except ValueError:
                s = str(line.strip())
                if "Valid data len X" in s:
                    l = s.split(":")
                    lenX = int(l[1].strip(' "\''))
                elif "Valid data len Y" in s:
                    l = s.split(":")
                    lenY = int(l[1].strip(' "\''))
                else: pass

        offset = abs(lowest) #we'll add this to every height value, then scale then add baseThickness
        expectedFacets = 4*(lenX-1)*(lenY-1) + 6*lenX + 6*lenY - 14

        print("Input File:      "+file.name)
        print("Output File:     "+outfile.name)
        print("Data points:     "+str(len(rawHeights)))
        print("X Length:        %d" % lenX)
        print("Y Length:        %d" % lenY)
        print("Z Scale:         " + str(zScale))
        print("nm / sample      "+ str(nmPerSample))
        print("Facets Expected: "+ str(expectedFacets))
        print("Lowest Point:    "+str(lowest))
        print("Offset:          "+str(offset))
        answer = input("\n Sound good (Y/N): ")
        done = (answer.lower() == 'y')

    #CREATE HEADER FOR STL FILE
    header = "solid " + modelName + "\n"
    outfile.write(header)

    #PUT HEIGHT VALUES FROM FILE INTO ARRAY
    fileLength = len(rawHeights)    #should be 40,000 lines
    print(fileLength)
    fileLoc = 0    #start at the beginning, first line
    heights = []    #will be a 2D array, 200 by 200
    for line in range(0,lenY):
        row = []    #will be a 1D array
        for column in range(0,lenX):
            #print(fileLoc)
            height = ((rawHeights[fileLoc] + offset)*zScale) + baseThickness    # add offset to height and scale it
            v = Vertex( (float(column)*nmPerSample), (float(line)*nmPerSample), float(height)) #make a Vertex object
            fileLoc += 1
            row.append(v)   #make this an array of objects
            #row.append(height)
        heights.append(row) #make this a 2D array of objects


    print(len(heights))
    print(len(heights[0]))


    #MAKE EXPANDED ARRAY
    expHeights = []
    for line in heights:
        yCoord = heights.index(line)

        expHeights.append(line)
        newRow = []
        for pt in line:  #pt is a Vertex object
            xCoord  = line.index(pt)

            try:
                nextPt  = line[xCoord+1]
                pt2     = heights[yCoord+1][xCoord]
                nextPt2 = heights[yCoord+1][xCoord+1]
            except IndexError:
                break

            newX = (pt.x + (nmPerSample/2))
            newY = (pt.y + (nmPerSample/2))
            newZ = (pt.z + nextPt.z + pt2.z + nextPt2.z) / 4    #avg of z values

            v = Vertex(newX, newY, newZ)
            newRow.append(v)

        if newRow != []: expHeights.append(newRow)

    #debugging code
    # print("number of lines: ", len(expHeights))
    # print("odd line len: ", len(expHeights[0]))
    # print("even line len: ", len(expHeights[1]))
    # print("odd line len: ", len(expHeights[2]))
    # print("even line len: ", len(expHeights[3]))
    # print("399th line (last line)", len(expHeights[len(expHeights)-1]))
    # print("398th line (next to last line)", len(expHeights[len(expHeights)-2]))


    #MAKE THE FLOOR
    for line in expHeights:
        yIndex = expHeights.index(line)
        if yIndex == 0:
            for pt in line: #pt is Vertex object
                xIndex = line.index(pt)
                if xIndex != len(line)-1:
                    # access the Vertex objects to pass to output function
                    va      = copy.deepcopy(pt)# Vertex(pt.x, pt.y, pt.z)
                    #vAlias  = expHeights[yIndex+2][len(line)-1]
                    vb      = copy.deepcopy(expHeights[yIndex+2][len(line)-1]) #Vertex(vAlias.x, vAlias.y, vAlias.z)
                    #vAlias  = expHeights[yIndex][xIndex+1]
                    vc      = copy.deepcopy(expHeights[yIndex][xIndex+1])#Vertex(vAlias.x, vAlias.y, vAlias.z)
                    va.z    = 0.0  # make z 0 (floor is at zero)
                    vb.z    = 0.0  # make z 0 also
                    vc.z    = 0.0  # also zero

                    # actually output stuff to the STL file
                    text = ""#"bottom facet "+str((xIndex+1)*(yIndex+1))+"\n"
                    text+= makeFacet(va, vb, vc)
                    outfile.write(text)

        elif yIndex == len(expHeights)-1:
            for pt in line:
                xIndex = line.index(pt)
                if xIndex != len(line)-1:
                    # access the Vertex objects to pass to output function
                    va      = copy.deepcopy(pt)#Vertex(pt.x, pt.y, pt.z)
                    #vAlias  = expHeights[yIndex][xIndex+1]
                    vb      = copy.deepcopy(expHeights[yIndex][xIndex+1])#Vertex(vAlias.x, vAlias.y, vAlias.z)#
                    #vAlias  = expHeights[yIndex-2][0]
                    vc      = copy.deepcopy(expHeights[yIndex-2][0])#Vertex(vAlias.x, vAlias.y, vAlias.z)#
                    va.z    = 0.0  # make z 0 (floor is at zero)
                    vb.z    = 0.0  # make z 0 also
                    vc.z    = 0.0  # also zero

                    # actually output stuff to the STL file
                    text = ""#"bottom facet "+str((xIndex+1)*(yIndex+1))+"\n"
                    text+= makeFacet(va, vb, vc)
                    outfile.write(text)
        elif yIndex % 2 == 0:   # even index value means real data
            va = copy.deepcopy(expHeights[yIndex][0])
            vb = copy.deepcopy(expHeights[yIndex][len(line)-1])
            vc = copy.deepcopy(expHeights[yIndex-2][0])
            va.z    = 0.0  # make z 0 (floor is at zero)
            vb.z    = 0.0  # make z 0 also
            vc.z    = 0.0  # also zero

            # actually output stuff to the STL file
            text = ""#"bottom facet "+str((xIndex+1)*(yIndex+1))+"\n"
            text+= makeFacet(va, vb, vc)
            outfile.write(text)

            va = copy.deepcopy(expHeights[yIndex][0])
            vb = copy.deepcopy(expHeights[yIndex+2][len(line)-1])
            vc = copy.deepcopy(expHeights[yIndex][len(line)-1])
            va.z    = 0.0  # make z 0 (floor is at zero)
            vb.z    = 0.0  # make z 0 also
            vc.z    = 0.0  # also zero

            # actually output stuff to the STL file
            text = ""#"bottom facet "+str((xIndex+1)*(yIndex+1))+"\n"
            text+= makeFacet(va, vb, vc)
            outfile.write(text)

        else:
            pass

    # MAKE EDGES / SIDES
    for line in expHeights:
        yIndex = expHeights.index(line)
        if yIndex == 0: # "front"
            for pt in line:
                xIndex = line.index(pt)
                try:
                    va = copy.deepcopy(line[xIndex+1])
                except IndexError:
                    break
                vb = copy.deepcopy(pt)
                vb.z = 0

                vc = copy.deepcopy(va)
                vc.z = 0

                va2 = va
                vb2 = pt
                vc2 = vb
                # actually output stuff to the STL file
                text = ""#"front facet set "+str(xIndex+1)+"\n"
                text+= makeFacet(va, vb, vc)
                text+= makeFacet(va2, vb2, vc2)
                outfile.write(text)

        elif yIndex == len(expHeights)-1: # "back"
            for pt in line:
                xIndex = line.index(pt)
                try:
                    va = copy.deepcopy(line[xIndex+1])
                except IndexError:
                    break
                vb = copy.deepcopy(va)
                vb.z = 0

                vc = copy.deepcopy(pt)
                vc.z = 0


                va2 = va
                vb2 = vc
                vc2 = pt
                # actually output stuff to the STL file
                text = ""#"back facet set "+str(xIndex+1)+"\n"
                text+= makeFacet(va, vb, vc)
                text+= makeFacet(va2, vb2, vc2)
                outfile.write(text)

        else:
            pass

        if yIndex % 2 == 0: # "left & right sides"
            try:
                va = copy.deepcopy(expHeights[yIndex+2][0]) #must do +2 to skip the imaginary points
            except IndexError:
                break
            # left side
            vb = copy.deepcopy(va)
            vb.z = 0
            vc = copy.deepcopy(line[0])
            vc.z = 0

            va2 = va
            vb2 = vc
            vc2 = vc    #line[0]

            #right side
            try:
                va3 = copy.deepcopy(expHeights[yIndex+2][len(line)-1])  #must do +2 to skip the imaginary points
            except IndexError:
                break
            vb3 = copy.deepcopy(line[len(line)-1])
            vb3.z = 0
            vc3 = copy.deepcopy(va3)
            vc3.z = 0

            va4 = va3
            vb4 = copy.deepcopy(line[len(line)-1])
            vc4 = copy.deepcopy(vb4)
            vc4.z = 0.0

            # actually output stuff to the STL file
            text = ""#"side facet set "+str(yIndex/2+1)+"\n"
            text+= makeFacet(va, vb, vc)
            text+= makeFacet(va2, vb2, vc2)
            text+= makeFacet(va3, vb3, vc3)
            text+= makeFacet(va4, vb4, vc4)
            outfile.write(text)



    # NOW FOR THE SURFACE CONTOURS (HERE WE GO)
    for line in expHeights:
        yIndex = expHeights.index(line)
        try:
            nextLine = expHeights[yIndex+1]     # this is a made up line
            nextNextLine = expHeights[yIndex+2] # this is a line with real data
        except IndexError:
            break
        if yIndex % 2 == 0: # we're on a line with real data

            for pt in line:
                xIndex = line.index(pt)
                try:
                    nextPt = line[xIndex+1]
                except IndexError:
                    break
                vSW     = pt                    #copy.deepcopy(pt)
                vNW     = nextNextLine[xIndex]  #copy.deepcopy(nextNextLine[xIndex])
                vNE     = nextNextLine[xIndex+1]#copy.deepcopy(nextNextLine[xIndex+1])
                vSE     = line[xIndex+1]        #copy.deepcopy(line[xIndex+1])
                vCent   = nextLine[xIndex]      #copy.deepcopy(nextLine[xIndex])

                # make the four facets
                text = ""#"surface facet set "+str((xIndex+1)*((yIndex/2)+1))+"\n"
                text+= makeFacet(vSW, vCent, vNW)   # West facet
                text+= makeFacet(vNW, vCent, vNE)   # North facet
                text+= makeFacet(vNE, vCent, vSE)   # East facet
                text+= makeFacet(vSE, vCent, vSW)   # South facet
                outfile.write(text)

        else:   # this is our made up line, don't fool with it
            pass

    #END STL FILE
    end = "endsolid " + modelName + "\n"

    outfile.write(end)
    outfile.close()
    print("\nAll done! Your file is at %s" % outfile.name)
    print("Expect %d facets." % expectedFacets)
    print("Model has %d facets." % facetCount)
    file.close()

#-------------------------------------------------------------------------------
def makeFacet(va,vb,vc):
    '''
    @param va: first Vertex object
    @param vb: next Vertex in order following right hand rule
    @param vc: next Vertex in order following right hand rule

    Takes Vertex objects and creates STL formatted text output.
    Describe/order points using the right hand rule.
    Output is in the following format (normal is not calculated):

    facet normal ni nj nk
    outer loop
        vertex v1x v1y v1z
        vertex v2x v2y v2z
        vertex v3x v3y v3z
    endloop
    endfacet'''
    v1 = [ va.x, va.y, va.z ]
    v2 = [ vb.x, vb.y, vb.z ]
    v3 = [ vc.x, vc.y, vc.z ]



    out  = " facet normal 0 0 0\n"
    out += " outer loop \n"
    out += "  vertex "+str(v1[0])+" "+str(v1[1])+" "+str(v1[2])+"\n"
    out += "  vertex "+str(v2[0])+" "+str(v2[1])+" "+str(v2[2])+"\n"
    out += "  vertex "+str(v3[0])+" "+str(v3[1])+" "+str(v3[2])+"\n"
    out += " endloop\n"
    out += " endfacet\n"

    global facetCount
    facetCount += 1

    return out
#-------------------------------------------------------------------------------
if __name__ == '__main__':
    main()
