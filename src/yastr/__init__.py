from pytest import main as pytest_main


def main():
    pytest_main(plugins=['yastr.plugin'])
