import lyricwikia
import argparse
import sys
import os
import shutil

# Define some command line arguments
parser = argparse.ArgumentParser(description='Download lyrics from LyricsWikia')
parser.add_argument('-i', '--input', type=str, help='Input file dataset')
parser.add_argument('-o', '--output', type=str, help='Output directory')
parser.add_argument('-s', '--skipHeader', action='store_true', help='Wether or not the file contains an header which should be skipped')

args = parser.parse_args()

# Thanks to https://gist.github.com/vladignatyev/06860ec2040cb497f0f3
def progress(count, total, status=''):
  bar_len = 60
  filled_len = int(round(bar_len * count / float(total)))

  percents = round(100.0 * count / float(total), 1)
  bar = '=' * filled_len + '-' * (bar_len - filled_len)

  sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', status))
  sys.stdout.flush()  # As suggested by Rom Ruben (see: http://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console/27871113#comment50529068_27871113)

def songs_count(path):
  with open(path) as f:
    count = len(f.readlines()) - 1
    if args.skipHeader:
      count -= 1
    return count

# Generator function which reads the lyrics from a csv file line by line
def lyric_entries_generator(path):
  with open(path) as lp:
    l = lp.readline()
    if args.skipHeader:
      l = lp.readline()
    while l:
      yield l.rstrip().split(',')
      l = lp.readline()

def create_output_dir(path):
  if os.path.exists(path) and os.path.isdir(path):
    shutil.rmtree(path)
  os.makedirs(path)


LOG_FILE = '.'.join([sys.argv[0], 'log'])
try:
  os.remove(os.path.join('.', LOG_FILE))
except OSError:
  # Log file did not exists...not too bad
  pass

def err(msg):
  with open(os.path.join('.', LOG_FILE), 'a') as log:
    log.write(msg)
    log.write('\n')

def download_lyric(song):
  try:
    lyric = lyricwikia.get_lyrics(song[1], song[2])
    filename = '_'.join([song[3], song[1], song[2]])
    filename = filename.replace('/', '-') # The '/' should never appear
    with open(os.path.join(args.output, filename), 'w') as sfile:
      sfile.write(lyric)
      return True
  except lyricwikia.LyricsNotFound:
    err('Could not download {}'.format(song))
    return False

if __name__ == '__main__':
  # Get the number of songs we are going to download
  totalSongs = songs_count(args.input)

  # Create output directory
  create_output_dir(args.output)

  # Download songs
  count = 0
  errCount = 0
  for lyric in lyric_entries_generator(args.input):
    progress(count, totalSongs, 'Errors encountered: {}'.format(errCount))
    if not download_lyric(lyric):
      errCount += 1
    count += 1

