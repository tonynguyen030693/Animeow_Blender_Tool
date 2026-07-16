try:
    import batchMode_combine as batch
    print('--------Start--------')
except Exception as e:
    print('import Error as : {}'.format(e))
try:
    batch.run()
except Exception as e:
    print('Error from Run as: {}'.format(e))
    input("Press enter to continue...")
