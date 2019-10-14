def list (list, conjunction):
    if len (list) == 0:
        return ''
    elif len (list) == 1:
        return list[0]
    else:
        list_string = ''
        for i in range (len (list) - 1):
            list_string += '\'{0}\', '.format (list[i])
        list_string = list_string[:-2]
        list_string += ' {0} \'{1}\''.format (conjunction, list[-1])
        return list_string
