import mutagen.ac3
import mutagen.apev2
from mutagen._util import loadfile


class AC3APEv2(mutagen.ac3.AC3):
    """An AC-3 or E-AC-3 file with APEv2 tags.

    Mutagen reads the stream information of AC-3 files but does not
    support tags for them. Other taggers (e.g. foobar2000 and MusicBrainz
    Picard) append an APEv2 tag to the stream, so we read and write that.
    """

    @loadfile()
    def load(self, filething):
        fileobj = filething.fileobj
        fileobj.seek(0)
        self.info = mutagen.ac3.AC3Info(fileobj)

        try:
            self.tags = mutagen.apev2.APEv2(fileobj)
        except mutagen.apev2.APENoHeaderError:
            self.tags = None
            return

        # Mutagen guesses the length from the size of everything after
        # the first frame header, which includes the appended tag.
        if self.info.bitrate:
            data = mutagen.apev2._APEv2Data(fileobj)
            if data.start is not None and not data.is_at_start:
                tag_size = fileobj.seek(0, 2) - data.start
                self.info.length -= 8.0 * tag_size / self.info.bitrate

    def add_tags(self):
        if self.tags is None:
            self.tags = mutagen.apev2.APEv2()
        else:
            raise mutagen.ac3.AC3Error(f"{self!r} already has tags: {self.tags!r}")
