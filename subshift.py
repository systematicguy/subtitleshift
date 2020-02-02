dangerous_ext = [".avi", ".mp4", ".mkv"]
import sys, os

        
class LineProvider(object):
    def __init__(self, lines):
        self.lines = lines
        self.idx = 0
    
    def next_line(self):
        res = self.lines[self.idx]
        self.idx += 1
        return res
        
    def next_line_group(self):
        res = []
        try:
            while True:
                next_line = self.next_line()
                if next_line.strip() == "":
                    break
                else:
                    res.append(next_line)
        except:
            pass
        return res
        
    def has_more(self):
        try:
            l = self.lines[self.idx]
            return True
        except:
            return False


def pad_zeros(i, digits):
    return str(i).zfill(digits)

    
class TimeStamp(object):
    def __init__(self, time_str):
        hours_minutes_secs, self.milliseconds = time_str.split(",", 1)
        self.milliseconds = int(self.milliseconds)
        hours, minutes, seconds = (int(e) for e in hours_minutes_secs.split(":"))
        self.milliseconds += seconds * 1000
        self.milliseconds += minutes * 60 * 1000
        self.milliseconds += hours * 60 * 60 * 1000
        
    def shift_by_milliseconds(self, ms):
        self.milliseconds += ms
    
    def get_representation(self):
        t = self.milliseconds
        res_milliseconds = t % 1000
        t /= 1000
        res_seconds = t % 60
        t /= 60
        res_minutes = t % 60
        t /= 60
        res_hours = t
        return "{}:{}:{},{}".format(
            pad_zeros(res_hours, 2),
            pad_zeros(res_minutes, 2),
            pad_zeros(res_seconds, 2),
            pad_zeros(res_milliseconds, 3)
        )

    def __str__(self):
        return self.get_representation()

        
class Entry(object):
    def __init__(self, index_line, time_line, content_lines):
        self.index_line = index_line
        times = time_line.split("-->")
        self.timestamps = [TimeStamp(time_str=s.strip()) for s in time_line.split("-->")]
        self.lines = content_lines
        
    def shift_by_milliseconds(self, ms):
        for ts in self.timestamps:
            ts.shift_by_milliseconds(ms)

    def get_representation(self):
        res = self.index_line
        res += "{} --> {}\n".format(self.timestamps[0], self.timestamps[1])
        res += "".join(self.lines)
        return res
        
    def __str__(self):
        return self.get_representation()

        
class Subtitle(object):
    def __init__(self, lines):
        lp = LineProvider(lines)
        self.entries = []
        while lp.has_more():
            try:
                line_group = lp.next_line_group()
                if line_group:
                    self.entries.append(Entry(
                        index_line=line_group[0],
                        time_line=line_group[1],
                        content_lines=line_group[2:]
                    ))
            except Exception as e:
                print("last successful Entry:\n{}\n".format(self.entries[-1]))
                print("failed to process:\n{}\n".format(line_group))
                raise
    
    def shift_by_milliseconds(self, ms):
        for e in self.entries:
            e.shift_by_milliseconds(ms)
            
    def get_representation(self):
        return "\n".join(str(e) for e in self.entries)+"\n"

        
if __name__ == "__main__":
    file_name = sys.argv[1]
    print("subtitle file: {}".format(file_name))
    ms = int(sys.argv[2])
    print("milliseconds: {}".format(ms))
    ext = os.path.splitext(file_name)[1]
    if ext.lower() in dangerous_ext:
        raw_input("Do you really want to work with this file? extension: {}".format(ext))
    with open(file_name) as f:
        lines = f.readlines()
    sub = Subtitle(lines)
    sub.shift_by_milliseconds(ms)
    with open(file_name, "w") as f:
        f.write(sub.get_representation())
    
        
    
            
    
    
            
    