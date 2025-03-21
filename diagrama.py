import os
import datetime
from typing import List, Dict, Optional

class Produto:
    """
    Classe que representa um produto da loja de roupas.
    """
    def __init__(self, id: int, nome: str, tamanho: str, cor: str, quantidade: int, preco: float, limite_minimo: int = 5):
        self.id = id
        self.nome = nome
        self.tamanho = tamanho
        self.cor = cor
        self.quantidade = quantidade
        self.preco = preco
        self.limite_minimo = limite_minimo

    def __str__(self) -> str:
        return f"ID: {self.id} | {self.nome} | Tamanho: {self.tamanho} | Cor: {self.cor} | Quantidade: {self.quantidade} | Preço: R${self.preco:.2f}"

    def atualizar_quantidade(self, quantidade: int) -> None:
        """Atualiza a quantidade do produto no estoque."""
        self.quantidade += quantidade

    def verificar_estoque_baixo(self) -> bool:
        """Verifica se o produto está com estoque baixo."""
        return self.quantidade < self.limite_minimo


class Venda:
    """
    Classe que representa uma venda realizada na loja.
    """
    def __init__(self, id: int, produtos: Dict[int, int], data: datetime.datetime = None):
        self.id = id
        self.produtos = produtos  # Dicionário com {id_produto: quantidade}
        self.data = data if data else datetime.datetime.now()
        self.valor_total = 0.0

    def __str__(self) -> str:
        return f"Venda #{self.id} | Data: {self.data.strftime('%d/%m/%Y %H:%M')} | Valor: R${self.valor_total:.2f}"

    def calcular_valor_total(self, produtos: Dict[int, Produto]) -> None:
        """Calcula o valor total da venda."""
        self.valor_total = sum(produtos[id_produto].preco * quantidade 
                           for id_produto, quantidade in self.produtos.items())


class Estoque:
    """
    Classe que gerencia o estoque de produtos.
    """
    def __init__(self):
        self.produtos: Dict[int, Produto] = {}
        self.vendas: List[Venda] = []
        self.ultimo_id_produto = 0
        self.ultimo_id_venda = 0

    def adicionar_produto(self, nome: str, tamanho: str, cor: str, quantidade: int, preco: float, limite_minimo: int = 5) -> Produto:
        """Adiciona um novo produto ao estoque."""
        self.ultimo_id_produto += 1
        produto = Produto(self.ultimo_id_produto, nome, tamanho, cor, quantidade, preco, limite_minimo)
        self.produtos[self.ultimo_id_produto] = produto
        return produto

    def atualizar_produto(self, id_produto: int, nome: str = None, tamanho: str = None, 
                         cor: str = None, quantidade: int = None, preco: float = None, 
                         limite_minimo: int = None) -> Optional[Produto]:
        """Atualiza as informações de um produto existente."""
        if id_produto not in self.produtos:
            return None
        
        produto = self.produtos[id_produto]
        
        if nome:
            produto.nome = nome
        if tamanho:
            produto.tamanho = tamanho
        if cor:
            produto.cor = cor
        if quantidade is not None:
            produto.quantidade = quantidade
        if preco is not None:
            produto.preco = preco
        if limite_minimo is not None:
            produto.limite_minimo = limite_minimo
            
        return produto

    def remover_produto(self, id_produto: int) -> bool:
        """Remove um produto do estoque."""
        if id_produto in self.produtos:
            del self.produtos[id_produto]
            return True
        return False

    def registrar_venda(self, produtos_vendidos: Dict[int, int]) -> Optional[Venda]:
        """
        Registra uma nova venda.
        O parâmetro produtos_vendidos é um dicionário com {id_produto: quantidade}
        """
        # Verifica se todos os produtos existem e têm quantidade suficiente
        for id_produto, quantidade in produtos_vendidos.items():
            if id_produto not in self.produtos:
                print(f"Erro: Produto com ID {id_produto} não existe.")
                return None
            if self.produtos[id_produto].quantidade < quantidade:
                print(f"Erro: Produto {self.produtos[id_produto].nome} tem apenas {self.produtos[id_produto].quantidade} unidades em estoque.")
                return None
        
        # Atualiza o estoque
        for id_produto, quantidade in produtos_vendidos.items():
            self.produtos[id_produto].atualizar_quantidade(-quantidade)
            
            # Verifica se o estoque ficou baixo
            if self.produtos[id_produto].verificar_estoque_baixo():
                print(f"ALERTA: Estoque baixo para {self.produtos[id_produto].nome} (Quantidade: {self.produtos[id_produto].quantidade})")
        
        # Cria a venda
        self.ultimo_id_venda += 1
        venda = Venda(self.ultimo_id_venda, produtos_vendidos)
        venda.calcular_valor_total(self.produtos)
        self.vendas.append(venda)
        
        return venda

    def listar_produtos(self) -> List[Produto]:
        """Retorna a lista de todos os produtos no estoque."""
        return list(self.produtos.values())

    def listar_produtos_estoque_baixo(self) -> List[Produto]:
        """Retorna a lista de produtos com estoque baixo."""
        return [produto for produto in self.produtos.values() if produto.verificar_estoque_baixo()]

    def gerar_relatorio_estoque(self) -> str:
        """Gera um relatório do estoque atual."""
        relatorio = "===== RELATÓRIO DE ESTOQUE =====\n"
        relatorio += f"Data: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
        relatorio += f"Total de produtos: {len(self.produtos)}\n\n"
        
        for produto in sorted(self.produtos.values(), key=lambda p: p.nome):
            status = "ESTOQUE BAIXO" if produto.verificar_estoque_baixo() else "OK"
            relatorio += f"{produto} | Status: {status}\n"
            
        return relatorio

    def gerar_relatorio_vendas(self, data_inicio: datetime.datetime = None, data_fim: datetime.datetime = None) -> str:
        """Gera um relatório de vendas no período especificado."""
        if data_inicio is None:
            data_inicio = datetime.datetime.min
        if data_fim is None:
            data_fim = datetime.datetime.max
            
        vendas_periodo = [venda for venda in self.vendas 
                          if data_inicio <= venda.data <= data_fim]
        
        relatorio = "===== RELATÓRIO DE VENDAS =====\n"
        relatorio += f"Período: {data_inicio.strftime('%d/%m/%Y') if data_inicio != datetime.datetime.min else 'Início'} "
        relatorio += f"a {data_fim.strftime('%d/%m/%Y') if data_fim != datetime.datetime.max else 'Hoje'}\n"
        relatorio += f"Total de vendas: {len(vendas_periodo)}\n"
        relatorio += f"Valor total: R${sum(venda.valor_total for venda in vendas_periodo):.2f}\n\n"
        
        for venda in vendas_periodo:
            relatorio += f"{venda}\n"
            relatorio += "Produtos vendidos:\n"
            for id_produto, quantidade in venda.produtos.items():
                if id_produto in self.produtos:
                    produto = self.produtos[id_produto]
                    relatorio += f"  - {quantidade}x {produto.nome} (Tamanho: {produto.tamanho}, Cor: {produto.cor}) - R${produto.preco:.2f} cada\n"
                else:
                    relatorio += f"  - {quantidade}x Produto ID {id_produto} (não encontrado no estoque atual)\n"
            relatorio += "\n"
            
        return relatorio


class Interface:
    """
    Classe que implementa a interface de linha de comando para o sistema.
    """
    def __init__(self):
        self.estoque = Estoque()
        self.opcoes = {
            '1': self.cadastrar_produto,
            '2': self.atualizar_produto,
            '3': self.remover_produto,
            '4': self.listar_produtos,
            '5': self.registrar_venda,
            '6': self.listar_produtos_estoque_baixo,
            '7': self.gerar_relatorio_estoque,
            '8': self.gerar_relatorio_vendas,
            '0': self.sair
        }
        self.executando = True
        
        # Carrega alguns produtos para teste
        self._carregar_produtos_teste()

    def _carregar_produtos_teste(self):
        """Carrega alguns produtos para teste."""
        self.estoque.adicionar_produto("Camiseta Básica", "M", "Preta", 15, 49.90)
        self.estoque.adicionar_produto("Camiseta Básica", "G", "Preta", 10, 49.90)
        self.estoque.adicionar_produto("Camiseta Básica", "M", "Branca", 12, 49.90)
        self.estoque.adicionar_produto("Calça Jeans", "40", "Azul", 8, 129.90)
        self.estoque.adicionar_produto("Calça Jeans", "42", "Azul", 6, 129.90)
        self.estoque.adicionar_produto("Vestido Floral", "P", "Colorido", 5, 89.90)
        self.estoque.adicionar_produto("Vestido Floral", "M", "Colorido", 3, 89.90)
        self.estoque.adicionar_produto("Bermuda Tactel", "M", "Preta", 20, 59.90)

    def exibir_menu(self):
        """Exibe o menu principal."""
        os.system('cls' if os.name == 'nt' else 'clear')
        print("===== SISTEMA DE GESTÃO DE ESTOQUE - LOJA DE ROUPAS =====")
        print("1. Cadastrar Produto")
        print("2. Atualizar Produto")
        print("3. Remover Produto")
        print("4. Listar Produtos")
        print("5. Registrar Venda")
        print("6. Listar Produtos com Estoque Baixo")
        print("7. Gerar Relatório de Estoque")
        print("8. Gerar Relatório de Vendas")
        print("0. Sair")
        print("=" * 53)

    def executar(self):
        """Inicia a execução do sistema."""
        while self.executando:
            self.exibir_menu()
            opcao = input("Escolha uma opção: ")
            if opcao in self.opcoes:
                self.opcoes[opcao]()
            else:
                print("Opção inválida!")
                input("Pressione Enter para continuar...")

    def cadastrar_produto(self):
        """Cadastra um novo produto."""
        print("\n===== CADASTRAR PRODUTO =====")
        nome = input("Nome: ")
        tamanho = input("Tamanho: ")
        cor = input("Cor: ")
        
        quantidade = 0
        while quantidade <= 0:
            try:
                quantidade = int(input("Quantidade: "))
                if quantidade <= 0:
                    print("A quantidade deve ser maior que zero.")
            except ValueError:
                print("Valor inválido. Digite um número inteiro.")
        
        preco = 0
        while preco <= 0:
            try:
                preco = float(input("Preço: R$"))
                if preco <= 0:
                    print("O preço deve ser maior que zero.")
            except ValueError:
                print("Valor inválido. Digite um número.")
        
        limite_minimo = 5
        try:
            limite = input("Limite mínimo para alerta de estoque [5]: ")
            if limite:
                limite_minimo = int(limite)
        except ValueError:
            print("Valor inválido. Usando o valor padrão (5).")
        
        produto = self.estoque.adicionar_produto(nome, tamanho, cor, quantidade, preco, limite_minimo)
        print(f"\nProduto cadastrado com sucesso: {produto}")
        input("\nPressione Enter para continuar...")

    def atualizar_produto(self):
        """Atualiza informações de um produto existente."""
        print("\n===== ATUALIZAR PRODUTO =====")
        self.listar_produtos(pausar=False)
        
        try:
            id_produto = int(input("\nDigite o ID do produto que deseja atualizar: "))
            if id_produto not in self.estoque.produtos:
                print("Produto não encontrado!")
                input("Pressione Enter para continuar...")
                return
            
            produto = self.estoque.produtos[id_produto]
            print(f"\nAtualizando: {produto}")
            
            nome = input(f"Nome [{produto.nome}]: ")
            tamanho = input(f"Tamanho [{produto.tamanho}]: ")
            cor = input(f"Cor [{produto.cor}]: ")
            
            quantidade = None
            qtd_input = input(f"Quantidade [{produto.quantidade}]: ")
            if qtd_input:
                try:
                    quantidade = int(qtd_input)
                    if quantidade < 0:
                        print("A quantidade não pode ser negativa. Mantendo o valor atual.")
                        quantidade = None
                except ValueError:
                    print("Valor inválido. Mantendo o valor atual.")
            
            preco = None
            preco_input = input(f"Preço [R${produto.preco:.2f}]: ")
            if preco_input:
                try:
                    preco = float(preco_input)
                    if preco <= 0:
                        print("O preço deve ser maior que zero. Mantendo o valor atual.")
                        preco = None
                except ValueError:
                    print("Valor inválido. Mantendo o valor atual.")
            
            limite_minimo = None
            limite_input = input(f"Limite mínimo para alerta de estoque [{produto.limite_minimo}]: ")
            if limite_input:
                try:
                    limite_minimo = int(limite_input)
                    if limite_minimo < 0:
                        print("O limite não pode ser negativo. Mantendo o valor atual.")
                        limite_minimo = None
                except ValueError:
                    print("Valor inválido. Mantendo o valor atual.")
            
            produto = self.estoque.atualizar_produto(
                id_produto, 
                nome if nome else None, 
                tamanho if tamanho else None, 
                cor if cor else None, 
                quantidade, 
                preco, 
                limite_minimo
            )
            
            print(f"\nProduto atualizado com sucesso: {produto}")
            
        except ValueError:
            print("ID inválido!")
        
        input("\nPressione Enter para continuar...")

    def remover_produto(self):
        """Remove um produto do estoque."""
        print("\n===== REMOVER PRODUTO =====")
        self.listar_produtos(pausar=False)
        
        try:
            id_produto = int(input("\nDigite o ID do produto que deseja remover: "))
            
            if self.estoque.remover_produto(id_produto):
                print(f"Produto com ID {id_produto} removido com sucesso!")
            else:
                print(f"Produto com ID {id_produto} não encontrado!")
                
        except ValueError:
            print("ID inválido!")
            
        input("\nPressione Enter para continuar...")

    def listar_produtos(self, pausar=True):
        """Lista todos os produtos no estoque."""
        print("\n===== PRODUTOS EM ESTOQUE =====")
        produtos = self.estoque.listar_produtos()
        
        if not produtos:
            print("Nenhum produto cadastrado.")
        else:
            for produto in sorted(produtos, key=lambda p: p.id):
                status = "ESTOQUE BAIXO" if produto.verificar_estoque_baixo() else "OK"
                print(f"{produto} | Status: {status}")
        
        if pausar:
            input("\nPressione Enter para continuar...")

    def registrar_venda(self):
        """Registra uma nova venda."""
        print("\n===== REGISTRAR VENDA =====")
        self.listar_produtos(pausar=False)
        
        produtos_vendidos = {}
        
        while True:
            try:
                id_produto = input("\nDigite o ID do produto (ou deixe em branco para finalizar): ")
                
                if not id_produto:
                    break
                    
                id_produto = int(id_produto)
                
                if id_produto not in self.estoque.produtos:
                    print("Produto não encontrado!")
                    continue
                
                produto = self.estoque.produtos[id_produto]
                print(f"Selecionado: {produto.nome} | Tamanho: {produto.tamanho} | Cor: {produto.cor} | Preço: R${produto.preco:.2f}")
                
                quantidade = 0
                while quantidade <= 0 or quantidade > produto.quantidade:
                    try:
                        quantidade = int(input(f"Quantidade (disponível: {produto.quantidade}): "))
                        
                        if quantidade <= 0:
                            print("A quantidade deve ser maior que zero.")
                        elif quantidade > produto.quantidade:
                            print(f"Quantidade insuficiente em estoque. Disponível: {produto.quantidade}")
                            
                    except ValueError:
                        print("Valor inválido. Digite um número inteiro.")
                
                if id_produto in produtos_vendidos:
                    produtos_vendidos[id_produto] += quantidade
                else:
                    produtos_vendidos[id_produto] = quantidade
                    
                print(f"{quantidade}x {produto.nome} adicionado à venda.")
                
            except ValueError:
                print("ID inválido!")
        
        if not produtos_vendidos:
            print("Nenhum produto selecionado. Venda cancelada.")
            input("\nPressione Enter para continuar...")
            return
        
        # Mostra resumo da venda
        print("\n===== RESUMO DA VENDA =====")
        valor_total = 0
        
        for id_produto, quantidade in produtos_vendidos.items():
            produto = self.estoque.produtos[id_produto]
            subtotal = produto.preco * quantidade
            valor_total += subtotal
            print(f"{quantidade}x {produto.nome} (Tamanho: {produto.tamanho}, Cor: {produto.cor}) - R${produto.preco:.2f} cada - Subtotal: R${subtotal:.2f}")
        
        print(f"\nValor Total: R${valor_total:.2f}")
        
        confirmar = input("\nConfirmar venda? (S/N): ").strip().upper()
        
        if confirmar == 'S':
            venda = self.estoque.registrar_venda(produtos_vendidos)
            if venda:
                print(f"\nVenda #{venda.id} registrada com sucesso!")
                print(f"Valor total: R${venda.valor_total:.2f}")
        else:
            print("\nVenda cancelada.")
            
        input("\nPressione Enter para continuar...")

    def listar_produtos_estoque_baixo(self):
        """Lista produtos com estoque baixo."""
        print("\n===== PRODUTOS COM ESTOQUE BAIXO =====")
        produtos = self.estoque.listar_produtos_estoque_baixo()
        
        if not produtos:
            print("Não há produtos com estoque baixo.")
        else:
            for produto in sorted(produtos, key=lambda p: p.quantidade):
                print(f"{produto} | ALERTA: Estoque Baixo!")
                
        input("\nPressione Enter para continuar...")

    def gerar_relatorio_estoque(self):
        """Gera e exibe um relatório do estoque atual."""
        relatorio = self.estoque.gerar_relatorio_estoque()
        print("\n" + relatorio)
        
        salvar = input("\nDeseja salvar o relatório em arquivo? (S/N): ").strip().upper()
        
        if salvar == 'S':
            nome_arquivo = f"relatorio_estoque_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(nome_arquivo, 'w', encoding='utf-8') as arquivo:
                arquivo.write(relatorio)
            print(f"Relatório salvo como '{nome_arquivo}'")
            
        input("\nPressione Enter para continuar...")

    def gerar_relatorio_vendas(self):
        """Gera e exibe um relatório de vendas."""
        print("\n===== RELATÓRIO DE VENDAS =====")
        
        # Solicita período para o relatório
        print("Defina o período para o relatório (deixe em branco para considerar todo o período):")
        
        data_inicio = None
        data_fim = None
        
        try:
            data_inicio_str = input("Data inicial (DD/MM/AAAA): ")
            if data_inicio_str:
                data_inicio = datetime.datetime.strptime(data_inicio_str, "%d/%m/%Y")
                
            data_fim_str = input("Data final (DD/MM/AAAA): ")
            if data_fim_str:
                data_fim = datetime.datetime.strptime(data_fim_str, "%d/%m/%Y")
                # Ajusta para o final do dia
                data_fim = data_fim.replace(hour=23, minute=59, second=59)
                
        except ValueError:
            print("Formato de data inválido. Usando todo o período.")
            data_inicio = None
            data_fim = None
        
        relatorio = self.estoque.gerar_relatorio_vendas(data_inicio, data_fim)
        print("\n" + relatorio)
        
        salvar = input("\nDeseja salvar o relatório em arquivo? (S/N): ").strip().upper()
        
        if salvar == 'S':
            nome_arquivo = f"relatorio_vendas_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(nome_arquivo, 'w', encoding='utf-8') as arquivo:
                arquivo.write(relatorio)
            print(f"Relatório salvo como '{nome_arquivo}'")
            
        input("\nPressione Enter para continuar...")

    def sair(self):
        """Encerra a execução do sistema."""
        print("\nEncerrando o sistema...")
        self.executando = False


if __name__ == "__main__":
    # Inicializa e executa o sistema
    sistema = Interface()
    sistema.executar()
