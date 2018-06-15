import numpy as N
import os

def read_bundle( infile ):
  points = []
  bun_file = infile + 'data'
  os.path.getsize( bun_file )
  bytes = os.path.getsize( bun_file )
  num = bytes / 4

  num_count = 0
  f = open( bun_file , 'rb')
  while num_count < num:
    p = N.frombuffer( f.read( 4 ), dtype=N.int32 )[ 0 ] # numero de puntos de la fibra
    vertex = N.frombuffer( f.read( p * 3 * 4 ), dtype=N.float32 ).reshape( -1, 3 ) # lee coordenadas fibra
    points.append( vertex )
    num_count = num_count + 1 + ( p * 3 )

  f.close()

  return points

def write_bundle( outfile, points ):
  #write bundles file
  f = open( outfile + 'data','wb' )
  ncount = len( points )
  for i in xrange( ncount ):
    f.write(N.array( [ len( points[ i ] ) ], N.int32 ).tostring() )
    f.write( points[ i ].ravel().tostring() )

  f.close()

  # write minf file
  minf = """attributes = {\n    'binary' : 1,\n    'bundles' : %s,\n    'byte_order' : 'DCBA',\n    'curves_count' : %s,\n    'data_file_name' : '*.bundlesdata',\n    'format' : 'bundles_1.0',\n    'space_dimension' : 3\n  }"""
  open( outfile, 'w' ).write(minf % ( [ 'points', 0 ], ncount ) )

def getBundleNames( bundlefile ):
  #get center names from bundle file
  ns = dict()
  execfile( bundlefile, ns )
  bunlist = ns[ 'attributes' ][ 'bundles' ]
  centers_num = len( bunlist ) / 2
  labels = []
  for i in xrange( centers_num ):

    ind = i * 2
    labels.append( bunlist[ ind ] )
  return labels

def read_bundle_severalbundles( infile ):
  points = []
  bun_file = infile + 'data'
  os.path.getsize( bun_file )
  bytes = os.path.getsize( bun_file )
  num = bytes / 4

  ns = dict()
  execfile( infile, ns )
  bundlescount = ns[ 'attributes' ][ 'bundles' ]
  curvescount = ns[ 'attributes' ][ 'curves_count' ]
  bunnames = []
  bunstart = []
  bun_num = len( bundlescount ) / 2
  count = 0
  for i in xrange( bun_num ):

    bunnames.append( bundlescount[ count ] )
    count = count + 1
    bunstart.append( bundlescount[ count ] )
    count = count + 1
    points.append( [] )

  bun_size = []
  if len( bunstart ) > 1:

    for b in xrange( len( bunstart ) - 1 ):

      bun_size.append( bunstart[ b + 1 ] - bunstart[ b ] )
    bun_size.append( curvescount - bunstart[ b + 1 ] )
  else:

    bun_size.append( curvescount )
  num_count = 0
  f = open( bun_file )
  bun_count = 0
  num_count_bundle = 0
  while num_count < num:

    p = N.frombuffer( f.read( 4 ), 'i' )[ 0 ]
    vertex = N.frombuffer( f.read( p * 3 * 4 ), 'f' ).reshape( -1, 3 )
    points[ bun_count ].append( vertex )
    #print num_count, p, bun_count, num_count_bundle
    num_count_bundle = num_count_bundle + 1
    if num_count_bundle == bun_size[ bun_count ]:
      bun_count = bun_count + 1
      num_count_bundle = 0
    num_count = num_count + 1 + ( p * 3 )

  f.close()
  return points, bunnames


def write_bundle_severalbundles( outfile, points, bundles = [] ):
  #write bundles file
  f = open( outfile + 'data','w' )
  ncount = 0
  for i in xrange( len( points ) ):

    size = len( points[ i ] )
    ncount = ncount + size
    bun = points[ i ]
    for i in xrange( size ):

      f.write( N.array( [ len( bun[ i ] ) ], N.int32 ).tostring() )
      f.write( bun[ i ].ravel().tostring() )
  f.close()
  # wrtie minf file
  minf = """attributes = {\n    'binary' : 1,\n    'bundles' : %s,\n    'byte_order' : 'DCBA',\n    'curves_count' : %s,\n    'data_file_name' : '*.bundlesdata',\n    'format' : 'bundles_1.0',\n    'space_dimension' : 3\n  }"""

  bundles_list = []
  ind = 0
  for i in xrange( len( points ) ):

    if bundles == []:

      bundles_list.append( str( i ) )
    else:

      bundles_list.append( bundles[ i ] )
    bundles_list.append( ind )
    #print i, ' : len= ', len(points[i])
    ind = ind + len( points[ i ] )

  bundlesstr = '['
  l = len( bundles_list ) / 2
  for i in xrange( l - 1 ):

    ind = i*2
    bundlesstr += ' \'' + bundles_list[ ind ] + '\', ' \
                        + str( bundles_list[ ind + 1 ] ) + ','
  bundlesstr += ' \'' + bundles_list[ ind + 2 ] + '\', ' \
                      + str( bundles_list[ ind + 3 ] ) + ' ]'

  open( outfile, 'w' ).write( minf % ( bundlesstr, ncount ) )

