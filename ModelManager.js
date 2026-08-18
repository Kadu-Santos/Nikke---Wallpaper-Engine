/**
 * Gerencia o carregamento dos modelos do wallpaper.
 *
 * Responsabilidades:
 * - Carregar a lista de modelos (models.json)
 * - Carregar o config.json de um modelo
 * - Gerenciar a variante atual (default, cover, aim, etc.)
 * - Gerar os caminhos completos para os arquivos do Spine
 */
export default class ModelManager {

    // Cria uma nova instância do gerenciador.
    constructor(modelsPath = "models") {

        // Pasta raiz onde ficam todos os modelos.
        this.modelsPath = modelsPath;

        // Lista de modelos lida do arquivo models.json.
        this.modelsIndex = [];

        // Modelo atualmente carregado (registro do models.json).
        this.currentModel = null;

        // Configuração (config.json) do modelo atual.
        this.currentConfig = null;

        // Variante atualmente selecionada.
        this.currentVariant = null;

        // Índice da variante atualmente selecionada.
        this.currentVariantIndex = 0;

        // Índice do modelo atualmente selecionado.
        this.currentModelIndex = 0;

        // Textura/Skin atualmente selecionada (para modelos com múltiplas texturas).
        this.currentTextureIndex = 0;
    }

    // Carrega o arquivo models.json.
    async init() {
        const response = await fetch(`${this.modelsPath}/models.json`);
        const json = await response.json();
        this.modelsIndex = json.models || [];
    }

    // Carrega o primeiro modelo da lista
    async loadFirstModel() {
        if (this.modelsIndex.length === 0)
            return null;
        this.currentModelIndex = 0;
        return await this.loadModel(this.modelsIndex[0].id);
    }

    // Carrega um modelo aleatório
    async loadRandomModel() {
        if (this.modelsIndex.length === 0)
            return null;

        const random = Math.floor(Math.random() * this.modelsIndex.length);
        this.currentModelIndex = random;
        return await this.loadModel(this.modelsIndex[random].id);
    }

    // Retorna a lista de todos os modelos disponíveis.
    getModels() {
        return this.modelsIndex;
    }

    // Retorna o modelo atualmente carregado.
    getCurrentModel() {
        return this.currentModel;
    }

    // Retorna o config.json do modelo carregado.
    getCurrentConfig() {
        return this.currentConfig;
    }

    // Retorna a variante atualmente selecionada (aim, cover e default).
    getCurrentVariant() {
        return this.currentVariant;
    }

    // Retorna o ID da variante atualmente selecionada (aim, cover e default).
    getCurrentVariantId() {
        return this.currentVariant?.id ?? "default";
    }

    // Retorna a quantidade de texturas da variante atual.
    getTextureCount() {
        if (!this.currentVariant || !this.currentVariant.model)
            return 0;

        const textures =
            this.currentVariant.model.textures ??
            (this.currentVariant.model.texture ? [this.currentVariant.model.texture] : []);

        return textures.length;
    }

    // Retorna as configurações visuais do modelo atual (color1 e color2).
    getAppearance() {
        if (!this.currentConfig)
            return null;

        return this.currentConfig.appearance;
    }

    // Retorna a posição da variante atualmente selecionada.
    getCurrentPosition() {
        if (!this.currentVariant)
            return null;

        return this.currentVariant.position;
    }

    // Retorna uma animação específica.
    getAnimation(name) {
        if (!this.currentVariant || !this.currentVariant.animations)
            return null;

        return this.currentVariant.animations[name];
    }

    // Retorna a skin pelo índice.
    // Caso o índice seja inválido, retorna a primeira skin.
    getCurrentSkin(index = 0) {
        if (!this.currentVariant || !this.currentVariant.model)
            return null;

        const textures = this.currentVariant.model.textures;

        if (!textures || textures.length === 0)
            return null;

        if (index < 0 || index >= textures.length)
            return textures[0];

        return textures[index];
    }

    /**
     * Carrega um modelo pelo ID informado.
     */
    async loadModel(id) {
        // 1. Procura o índice correspondente para manter sincronizado com navegação manual
        const entryIndex = this.modelsIndex.findIndex(m => m.id === id);

        if (entryIndex === -1)
            throw new Error(`Model "${id}" not found.`);

        this.currentModelIndex = entryIndex;
        const entry = this.modelsIndex[entryIndex];

        // 2. Carrega o config.json do modelo
        const response = await fetch(`${this.modelsPath}/${entry.config}`);
        this.currentConfig = await response.json();
        this.currentModel = entry;

        // 3. Reseta estados críticos para evitar usar informações de skins antigas no novo modelo
        this.currentTextureIndex = 0;

        // 4. Inicia pela variante padrão
        this.setVariant("default");

        return this.currentConfig;
    }

    // Retorna o nome do modelo atualmente carregado.
    getCurrentModelName() {
        return this.currentConfig?.name ?? "";
    }

    /**
     * Define qual variante do modelo será utilizada.
     */
    setVariant(id) {
        if (!this.currentConfig || !this.currentConfig.variants)
            return null;

        const variantIndex = this.currentConfig.variants.findIndex(v => v.id === id);

        if (variantIndex === -1)
            throw new Error(`Variant "${id}" not found.`);

        this.currentVariantIndex = variantIndex;
        this.currentVariant = this.currentConfig.variants[variantIndex];

        return this.currentVariant;
    }
    
    trySetVariant(targetVariantId) {
        if (!this.currentConfig || !this.currentConfig.variants) return;

        const index = this.currentConfig.variants.findIndex(v => v.id.toLowerCase() === targetVariantId.toLowerCase());

        if (index !== -1) {
            // Achou a variante! Define o índice e O OBJETO.
            this.currentVariantIndex = index;
            this.currentVariant = this.currentConfig.variants[index];
        } else {
            // Não achou. Fallback pro default (índice 0) e define O OBJETO.
            this.currentVariantIndex = 0;
            this.currentVariant = this.currentConfig.variants[0];
        }
    }

    // Próximo modelo (Sincronizado)
    async nextModel() {
        if (this.modelsIndex.length === 0)
            return null;

        // Avança o índice imediatamente para evitar atropelos em cliques rápidos
        this.currentModelIndex++;
        if (this.currentModelIndex >= this.modelsIndex.length) {
            this.currentModelIndex = 0;
        }

        const targetModelId = this.modelsIndex[this.currentModelIndex].id;
        return await this.loadModel(targetModelId);
    }

    // Modelo anterior (Sincronizado)
    async previousModel() {
        if (this.modelsIndex.length === 0)
            return null;

        // Retrocede o índice imediatamente
        this.currentModelIndex--;
        if (this.currentModelIndex < 0) {
            this.currentModelIndex = this.modelsIndex.length - 1;
        }

        const targetModelId = this.modelsIndex[this.currentModelIndex].id;
        return await this.loadModel(targetModelId);
    }

    // Alterna para a próxima variante disponível.
    nextVariant() {
        if (!this.currentConfig || !this.currentConfig.variants)
            return this.currentVariant;

        const variants = this.currentConfig.variants;

        if (variants.length <= 1)
            return this.currentVariant;

        this.currentVariantIndex++;

        // Volta para a primeira variante ao chegar no fim.
        if (this.currentVariantIndex >= variants.length) {
            this.currentVariantIndex = 0;
        }

        this.currentVariant = variants[this.currentVariantIndex];

        return this.currentVariant;
    }

    // Retorna uma variante específica sem alterar a variante selecionada.
    getVariant(id) {
        if (!this.currentConfig || !this.currentConfig.variants)
            return null;
        return this.currentConfig.variants.find(v => v.id === id);
    }

    // Retorna se o modelo possui uma variante específica.
    hasVariant(id) {
        if (!this.currentConfig || !this.currentConfig.variants)
            return false;
        return this.currentConfig.variants.some(v => v.id === id);
    }

    // Retorna se o modelo atual possui mais de uma variante.
    canChangeVariant() {
        if (!this.currentConfig || !this.currentConfig.variants)
            return false;
        return this.currentConfig.variants.length > 1;
    }

    // Retorna o ícone de cada variante para os botões do player
    getVariantIcon() {
        if (!this.currentVariant)
            return "Defender.png";

        switch (this.currentVariant.id) {
            case "cover":
                return "Supporter.png";
            case "aim":
                return "Attacker.png";
            default:
                return "Defender.png";
        }
    }

    /**
     * Gera os caminhos completos dos arquivos do Spine para uma variante.
     */
    buildModelPaths(variant = null) {
        // Garantia de segurança se não houver variante passada ou definida
        const targetVariant = variant || this.currentVariant;

        if (!targetVariant || !this.currentModel) {
            return { skeleton: "", atlas: "", textures: [] };
        }

        // Resolvendo o sub-diretório de forma segura usando a propriedade 'folder'
        const subFolder = targetVariant.folder !== undefined ? targetVariant.folder : targetVariant.id;
        
        // Se for a variante default (e folder for vazio), usa apenas o caminho raiz da personagem
        const folder = (!subFolder || targetVariant.id === "default")
            ? `${this.modelsPath}/${this.currentModel.id}`
            : `${this.modelsPath}/${this.currentModel.id}/${subFolder}`;

        const model = targetVariant.model || {};
        
        // Filtra as texturas para ignorar chaves vazias ou nulas
        const rawTextures = model.textures ?? (model.texture ? [model.texture] : []);
        const filteredTextures = rawTextures.filter(Boolean);

        return {
            // Caminho completo do esqueleto (.skel)
            skeleton: `${folder}/${model.skeleton || ""}`,

            // Caminho completo do atlas (.atlas)
            atlas: `${folder}/${model.atlas || ""}`,

            // Caminho(s) completo(s) das texturas (.png)
            textures: filteredTextures.map(texture => `${folder}/${texture}`)
        };
    }
}