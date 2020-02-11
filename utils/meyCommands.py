import os
import shlex
import utils.common as utils_common

class meyCommands:
    def __init__(self, commands_folder_root, arg_parser = None):
        self.cmd_root = os.path.abspath(commands_folder_root)
        self.arg_parser = self.parse_arg if arg_parser is None else arg_parser

    def run(self, cmd, ctx = None):
        current_dir = self.cmd_root
        args = []
        queue_up = False
        for path in self.breakdown_command(cmd):
            tmp_cur = os.path.join(current_dir,path.lower())
            if queue_up:
                args.append(self.arg_parser(path))
            elif not os.path.exists(tmp_cur):
                queue_up = True
                current_dir = tmp_cur+'.py'
            else:
                current_dir = tmp_cur
        imp = utils_common.import_module(current_dir)
        return imp.main(ctx, *args)

    @staticmethod
    def parse_arg(arg):
        try:
            return int(arg)
        except:
            if len(arg) == 1:
                if arg.lower() in ('t','f'):
                    return arg.lower() == 't'
            else:
                if arg.lower() in ('true','false'):
                    return arg.lower() == 'true'
            return arg

    @staticmethod
    def breakdown_command(cmd):
        return shlex.split(cmd)