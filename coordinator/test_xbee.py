from xbee import Xbee
import filecmp # pragma: no cover

OUTPUT_DIR = "test_output/"

class TestXbeeTransmit:
    def setUp(self):
        self.xbee = Xbee()
        self.xbee.write_cb = self.write

    def open(self, file, mode):
        return open(OUTPUT_DIR + file, mode)

    def close(self):
        self.f.close()

    def compare(self, file):
        ifile = OUTPUT_DIR + file
        ofile = ifile+"_lastrun"
        output = open(ofile, "w")
        output.write(self.data)
        output.close()
        assert filecmp.cmp(ifile, ofile)

    def write(self, data):
        self.data = data

    def do_transmit(self):
        self.xbee.transmit(0xffff, 0xffff, "Hello")

    def do_at_command(self):
        self.xbee.at_command("D0" + chr(0x4))

    def do_at_command_remote(self):
        self.xbee.at_command_remote(0x123, 0xfffe, "D0" + chr(0x4))

    def test_at_command(self):
        self.do_at_command()
        self.compare("at_command")

    def test_at_command_remote(self):
        self.do_at_command_remote()
        self.compare("at_command_remote")

    def test_transmit(self):
        self.do_transmit()
        self.compare("transmit")

    def gen_output(self):
        self.setUp()

        f = self.open("transmit", "w")
        self.do_transmit()
        f.write(self.data)
        f.close()

        self.setUp()
        f = self.open("at_command", "w")
        self.do_at_command()
        f.write(self.data)
        f.close()
        print self.data

        self.setUp()
        f = self.open("at_command_remote", "w")
        self.do_at_command_remote()
        f.write(self.data)
        f.close()
        print self.data

if __name__ == "__main__":
    t = TestXbeeTransmit()
    t.gen_output()
