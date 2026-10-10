"""Tests for the bash completions in completions/."""
import os
import re
import shutil
import subprocess
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
# plugin -> the completion file that serves it; the packages link the others
COMPLETIONS = {
    "check_zyxel-cpu": "check_zyxel-cpu",
    "check_zyxel-mem": "check_zyxel-cpu",
    "check_zyxel-fan": "check_zyxel-fan",
    "check_zyxel-temperature": "check_zyxel-fan",
    "check_zyxel-voltage": "check_zyxel-fan",
    "check_zyxel-flash": "check_zyxel-flash",
    "check_zyxel-power": "check_zyxel-power",
    "check_zyxel-time": "check_zyxel-time",
}


def complete(plugin, *words):
    """The candidates bash offers for the last of words, which may be empty."""
    words = (plugin,) + words
    script = 'source "$1"; shift; COMP_WORDS=("$@"); COMP_CWORD=$(($# - 1)); ' \
             '$(complete -p "$1" | sed -E "s/.*-F ([^ ]+) .*/\\1/"); printf "%s\\n" "${COMPREPLY[@]}"'
    completion = os.path.join(ROOT, "completions", COMPLETIONS[plugin])
    result = subprocess.run(["bash", "-c", script, "bash", completion] + list(words),
                            capture_output=True, text=True, check=True)
    return [line for line in result.stdout.split("\n") if line]


def usage(plugin):
    """The usage text -h prints; -h exits UNKNOWN."""
    # run as ./plugin, $0 in the text must not look like an option
    return subprocess.run(["./" + plugin, "-h"], capture_output=True, text=True, cwd=ROOT).stdout


def usage_choices(plugin, option):
    """The values the usage text lists for option as a|b|c."""
    return re.search(r"\[%s ([^]<>]+)\]" % option, usage(plugin)).group(1).split("|")


@unittest.skipUnless(shutil.which("bash"), "bash is not installed")
class CompletionTests(unittest.TestCase):
    def test_syntax(self):
        for name in set(COMPLETIONS.values()):
            subprocess.run(["bash", "-n", os.path.join(ROOT, "completions", name)], check=True)

    def test_every_plugin_is_served(self):
        plugins = {name for name in os.listdir(ROOT) if name.startswith("check_zyxel-")}
        self.assertEqual(plugins, set(COMPLETIONS))

    def test_offers_exactly_the_options_of_getopts(self):
        for plugin in COMPLETIONS:
            with open(os.path.join(ROOT, plugin)) as script:
                optstring = re.search(r'getopts "([^"]+)"', script.read()).group(1)
            options = {"-" + letter for letter in optstring.replace(":", "")}
            self.assertEqual(set(complete(plugin, "")), options, plugin)

    def test_offers_exactly_the_options_of_usage(self):
        for plugin in COMPLETIONS:
            options = set(re.findall(r"(?:^|[\s\[])(-\w)\b", usage(plugin))) | {"-h"}
            self.assertEqual(set(complete(plugin, "")), options, plugin)

    def test_choices(self):
        for plugin in COMPLETIONS:
            for option in ("-V", "-l", "-a", "-x"):
                self.assertEqual(complete(plugin, option, ""), usage_choices(plugin, option),
                                 plugin + " " + option)
        self.assertEqual(complete("check_zyxel-cpu", "-l", "auth"), ["authNoPriv", "authPriv"])

    def test_no_candidates_for_values(self):
        for plugin in COMPLETIONS:
            for option in ("-C", "-p", "-u", "-A", "-X", "-t", "-r"):
                self.assertEqual(complete(plugin, option, ""), [], plugin + " " + option)
        self.assertEqual(complete("check_zyxel-flash", "-o", ""), [])
        self.assertEqual(complete("check_zyxel-voltage", "-i", ""), [])


if __name__ == "__main__":
    unittest.main()
