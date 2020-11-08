import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--bf', required=True, help='Binary file containing a single packet layer')
    parser.add_argument('--obyte', required=False, help='Oracle integer value to search for')
    parser.add_argument('--oint', required=False, help='Oracle integer value to search for')
    parser.add_argument('--obool', required=False, help='Oracle bool value to search for')
    parser.add_argument('--ofloat', required=False, help='Oracle float value to search for')
    parser.add_argument('--obytes', required=False, help='Oracle bytes value to search for')

    args = parser.parse_args()


if __name__ == '__main__':
    main()

