#!python3

from glob import glob
import sys
import re



DEBUG = False


def debug(*args):
    '''funciona como print, mas só é executada se sys.flags.debug == 1'''
    if not DEBUG:
        return ;
    print(*args)





# exemplo:
# void *variavel
re.tipoVariavel = r'\w+\**\s+\**\w+'
# exemplo:
# void *variavel, void *a, int b
re.parametrosFunc = r'(?:'+re.tipoVariavel+r'(?:\[.*?\])?\s*(?:,\s*)?)*'


def getFuncoes(content):
    '''retorna todas as funções:
    exemplo:
    (void *a(int b), int main(void), int vazio())'''
    return re.findall(re.compile(r'('+re.tipoVariavel+r'\s*\('+re.parametrosFunc+'\))\s*'), content)




def removerParteInutil(content):
    '''remove todos os comentários, conteudo dentro de {} e strings'''
    # removendo strings
    resultParcial = re.sub(re.compile(r'(["\'])(?:[^"\\]|\\.)*\1', re.DOTALL), '', content)

    # removendo os comentários de uma linha
    resultParcial = re.sub(re.compile(r'//(.*?)\n', re.DOTALL), '', resultParcial)

    # remove os comentários de /* */
    resultParcial = re.sub(re.compile(r'/\*.*?\*/', re.DOTALL), '', resultParcial)

    # removendo conteudo de {}
    result = ''
    chaveAberta = 0
    for ch in resultParcial:
        if ch == '{':
            chaveAberta += 1
            continue
        elif ch == '}':
            chaveAberta -= 1
            continue

        if chaveAberta == 0:
            # adiciona esse char ao resultado
            result += ch

    return result




def main():
    files = {
        'h': glob('*.h'),
        'c': glob('*.c')
    }
    
    # esse array possui pares de .c e .h
    # Exemplo: main.c main.h misc.c misc.h
    # filesPares = [
    #   (main.c, main.h),
    #   (misc.c, misc.h),
    # ]
    filesPares = []
    # para todos os arquivos .c que possuem .h
    for c in files['c']:
        basename = c[0:-2]
        h = basename+'.h'

        if h in files['h']:
            filesPares += [(c, h)]
        else:
            print('Arquivo "%s" encontrado, mas não foi encontrado o arquivo "%s".' % (c, h))


    if not files: # se estiver vazio
        print('Nenhum par de arquivo .c e .h encontrado.')
        sys.exit(0)


    for (c, h) in filesPares:
        # h é o fileName do arquivo .h
        # c é o fileName do arquivo .c

        print('\nCompletando arquivo "%s" com base no arquivo "%s".' % (h, c))

        # ponteiro do arquivo
        hFile = open(h, 'r', encoding='utf-8')
        cFile = open(c, 'r', encoding='utf-8')

        # os conteudos dos arquivos
        hContent = hFile.read()
        cContent = cFile.read()

        # condição do .h
        if hContent == '':
            # o arquivo .h estava vazio, vamos inicializar o arquivo
            # vamos supor o arquivo main.h
            # o ifndefVar será __MAIN_H__
            ifndefVar = '__'+h.replace('.', '_').upper()+'__'
            # vamos mudar o conteúdo para a forma padrão
            hContent = '#ifndef '+ifndefVar+'\n#define '+ifndefVar+'\n\n#endif // '+ifndefVar


        elif re.search(r'(#endif // \w+\s*)$', hContent, re.DOTALL) is None:
            print('O Arquivo "%s" não está no formato padrão. Siga este exemplo:\n\n' % h)
            print('#ifndef __FILE_H__')
            print('#define __FILE_H__\n')
            print('/* Content... */\n')
            print('#endif // __FILE_H__')
            sys.exit(0)


        # removendo os comentários
        hContentStripped = removerParteInutil(hContent)
        cContentStripped = removerParteInutil(cContent)

        cFuncoes = getFuncoes(cContentStripped)
        hFuncoes = getFuncoes(hContentStripped)

        debug('cFuncoes: %s\n' % ',\n'.join(cFuncoes))
        debug('hFuncoes: %s\n' % ',\n'.join(hFuncoes))


        for cFuncao in cFuncoes:
            if cFuncao in hFuncoes:
                # essa função já tá no .h, do msmo jeitão
                continue


            print('\tAdicionando função "%s" no arquivo "%s"' % (cFuncao, h))
            # vamos adicionar ao content
            # verificando se devo substituir ou se devo adicionar msmo

            # só procurar uma função parecida e substituir
            cFuncTipoName = re.match('('+re.tipoVariavel+')\s*\('+re.parametrosFunc+'\)', cFuncao).groups()[0]

            devoSubstituir = cFuncTipoName in hContentStripped
            if devoSubstituir:
                # atualizando a função no hContent
                hContent = re.sub(cFuncTipoName+'\s*\('+re.parametrosFunc+'\)', cFuncao, hContent)
            else:
                # adicionando ao fim do arquivo
                hContent = re.sub(r'(#endif // \w+\s*)$', cFuncao+r';\n\n\1', hContent, re.DOTALL+re.MULTILINE)


        
        # liberando os arquivos
        if DEBUG:
            print(hContent)

        hFile.close()
        cFile.close()

        # salvando alterações
        if not DEBUG:
            # atualizando o arquivo .h
            with open(h, 'w', encoding='utf-8') as hFile:
                hFile.write(hContent)



if __name__ == '__main__':
    main()