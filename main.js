import ModelManager from "./ModelManager.js"; // Importa o gerenciador de modelos
import SoundManager from "./SoundManager.js"; // Importa o gerenciador de som

// Cria instâncias dos gerenciadores de modelo e som
const modelManager = new ModelManager();
const soundManager = new SoundManager();

let canvas = null; // Elemento canvas para renderização
let reproductor = null; // Instância do Spine Player
let autoplayTimer = null; // Contador para o autoplay
let initialized = false; // Indica se a aplicação foi inicializada

function loadSpineRuntime(scriptUrl, globalName) {
    return new Promise((resolve, reject) => {
        if (window[globalName]) {
            resolve(window[globalName]);
            return;
        }

        const script = document.createElement("script");
        script.src = scriptUrl;
        script.async = true;
        script.onload = () => {
            if (window[globalName]) {
                resolve(window[globalName]);
            } else {
                reject(new Error(`Runtime do Spine não foi carregado: ${globalName}`));
            }
        };
        script.onerror = () => reject(new Error(`Falha ao carregar ${scriptUrl}`));
        document.head.appendChild(script);
    });
}

// Variáveis de estado das animações
let animationLocked = false; // Bloqueia as animações
let clickCount = 0; // Conta cliques do usuário
let clickTimeout = null; // Timeout para resetar o contador de cliques
let animationTimeout = null; // Timeout para aplicar a próxima animação
let lockTimeout = null; // Timeout para desbloquear as animações
let currentSkinIndex = 0; // Índice da skin atual
let preferredVariant = "default";

// Variáveis que definem propriedades padrão do WE
let autoplayEnabled = false; // Indica se o autoplay está ativado
let autoplayMode = "sequential"; // Modo de autoplay (sequencial ou aleatório)
let autoplayTime = 5; // Tempo entre cada iteração no autoplay
let isUpdatingModel = false;

// Função para inicializar a aplicação
async function init() {
    await modelManager.init(); // Inicializa o gerenciador de modelos
    await soundManager.init(); // Inicializa o gerenciador de som

    initialized = true; // Marca como inicializada

    // Descomentar para abrir no navegador, pois sem o walpaper engine, ele não carrega o modelo inicial
    //await modelManager.loadModel("c353");
    //await updateSpinePlayer();

    // Se o Wallpaper Engine já enviou propriedades enquanto carregávamos, aplica agora:
    if (initialProperties) {
        await applyProperties(initialProperties); // Aplica as propriedades iniciais
    }

    canvas = document.querySelector("#player-container"); // Seleciona o elemento canvas no DOM
    registerEvents(); // Registra os eventos do mouse
    addImage(); // Adiciona a imagem de logotipo
}

// Função para criar o Spine Player
async function createSpinePlayer() {
    if (modelManager.hasVariant(preferredVariant)) {
        modelManager.trySetVariant(preferredVariant);
    }

    const paths = modelManager.buildModelPaths();
    let SpineRuntime = null;

    try {
        const response = await fetch(paths.skeleton);
        const buffer = await response.arrayBuffer();
        const uintArray = new Uint8Array(buffer);

        const versionBytes = uintArray.slice(0, 16);
        const versionString = new TextDecoder().decode(versionBytes).replace(/\0/g, '');

        if (versionString.includes("4.1")) {
            SpineRuntime = await loadSpineRuntime("spine-player4.1.js", "spine41");
        } else if (versionString.includes("4.0") || versionString.includes("3.8") || versionString.includes("3.7")) {
            SpineRuntime = await loadSpineRuntime("spine-player.js", "spine");
        } else {
            // Fallback seguro: usa a runtime mais nova disponível.
            SpineRuntime = window.spine41 || window.spine;
        }
    } catch (error) {
        console.error("Erro ao tentar ler a versão do .skel:", error);
        SpineRuntime = window.spine41 || window.spine;
    }

    if (!SpineRuntime || !SpineRuntime.SpinePlayer) {
        console.error("Nenhum runtime do Spine disponível para renderizar o modelo.");
        return;
    }

    return new Promise((resolve) => {
        reproductor = new SpineRuntime.SpinePlayer("player-container", {
            skelUrl: paths.skeleton,
            atlasUrl: paths.atlas,
            animation: modelManager.getAnimation("idle"),
            showControls: false,
            alpha: true,
            premultipliedAlpha: true,
            update: customCameraUpdate,

            success(player) {
                const defaultPos = modelManager.getCurrentPosition();
                player.anrb_posxa = -defaultPos.x;
                player.nrb_posy = -defaultPos.y;
                player.nrb_zoom = 10.0 / defaultPos.scale;

                saveCurrentModel(modelManager.getCurrentModel().id);
                addSkinButton();
                updateModelNavLabel();
                _initReady = true;

                const skins = reproductor.skeleton.data.skins;
                let initialSkin = 0;

                if(skins.length > 1)
                    initialSkin = 1;

                applySkinByIndex(initialSkin);

                resolve(); // Libera o sistema: O modelo carregou perfeitamente
            },
            error(player, reason) {
                console.error("Falha ao carregar o modelo Spine:", reason);
                resolve(); // Libera o sistema mesmo com erro para não travar o app
            }
        });
    });
}

// Função para destruir o Spine Player
function destroySpinePlayer() {
    if (!reproductor)
        return;

    try {
        if (typeof reproductor.stopRendering === "function") {
            reproductor.stopRendering();
        }
    } catch (error) {
        console.warn("Erro ao parar o render do Spine:", error);
    }

    try {
        if (typeof reproductor.dispose === "function") {
            reproductor.dispose();
        }
    } catch (error) {
        console.warn("Erro ao descarregar o player do Spine:", error);
    }

    reproductor = null;
    if (canvas) {
        canvas.replaceChildren(); // Limpa os filhos do canvas
    }
}

// Função para atualizar o Spine Player
async function updateSpinePlayer() {
    if (isUpdatingModel)
        return;
    isUpdatingModel = true;

    try {
        _initReady = false;
        animationLocked = false;
        clickCount = 0;

        clearTimeout(animationTimeout);
        clearTimeout(lockTimeout);
        clearTimeout(clickTimeout);

        destroySpinePlayer();
        await createSpinePlayer();
        applyBackground();
        addButton();
    } finally {
        // Libera a trava apenas quando tudo terminar de carregar
        isUpdatingModel = false;
    }
}

// Função para aplicar o padrão de cores do background
function applyBackground() {
    const colors = modelManager.getAppearance();

    document.body.style.backgroundImage =
        `linear-gradient(to bottom right, ${colors.color1}, ${colors.color2})`;
}

// Função para atualizar o botão
function updateButton(button) {
    button.style.backgroundImage =
        `url("image/buttons/${modelManager.getVariantIcon()}")`;
}

function applySkinByIndex(index) {
    const skins = reproductor?.skeleton?.data?.skins;
    if (!skins || !skins.length)
        return;

    const safeIndex = Math.max(0, Math.min(index, skins.length - 1));
    currentSkinIndex = safeIndex;

    reproductor.skeleton.setSkinByName(skins[currentSkinIndex].name);
    reproductor.skeleton.setSlotsToSetupPose();
    reproductor.animationState.apply(reproductor.skeleton);
}

// Função para adicionar o botão que troca de skins
function addSkinButton() {
    const skins = reproductor.skeleton.data.skins;

    // Remove um botão antigo, caso exista.
    document.getElementById("change-skin-button")?.remove();

    // Não cria o botão se existir apenas uma skin.
    if (skins.length <= 1)
        return;

    const button = document.createElement("button");

    button.id = "change-skin-button";
    button.style.zIndex = "2";
    button.style.position = "absolute";
    button.style.right = "50px";
    button.style.bottom = "155px";
    button.style.width = "55px";
    button.style.height = "55px";
    button.style.border = "none";
    button.style.cursor = "pointer";
    button.style.backgroundColor = "transparent";
    button.style.backgroundSize = "contain";
    button.style.backgroundRepeat = "no-repeat";
    button.style.backgroundPosition = "center";
    button.style.transition = "transform 0.2s";
    button.style.backgroundImage = "url(image/buttons/Clothes.png)";

    button.onclick = (event) => {
        event.stopPropagation();
        const nextIndex = (currentSkinIndex + 1) % skins.length;
        applySkinByIndex(nextIndex);
    };

    document.body.appendChild(button);
}

// Função para adicionar o botão que troca de posição (aim, cover e default)
function addButton() {
    const buttonId = "change-position-button";

    // Remove o botão antigo para limpar qualquer evento pendente
    document.getElementById(buttonId)?.remove();

    // Se o modelo atual NÃO puder trocar de variante, encerra aqui
    if (!modelManager.canChangeVariant()) {
        return;
    }

    const button = document.createElement("button");
    button.id = buttonId;
    button.style.zIndex = "2";
    button.style.position = "absolute";
    button.style.right = "50px";
    button.style.bottom = "80px";
    button.style.width = "60px";
    button.style.height = "60px";
    button.style.border = "none";
    button.style.cursor = "pointer";
    button.style.backgroundColor = "transparent";
    button.style.backgroundSize = "contain";
    button.style.backgroundRepeat = "no-repeat";
    button.style.backgroundPosition = "center";
    button.style.transition = "transform 0.2s";

    button.onclick = (event) => {
        event.stopPropagation();
        modelManager.nextVariant();
        preferredVariant = modelManager.getCurrentVariantId();
        updateSpinePlayer();
    };

    document.body.appendChild(button);
    updateButton(button);
}

// Função para adicionar a imagem
function addImage() {
    if (!document.getElementById("nikke-logo")) {
        const logo = document.createElement("img");
        logo.id = "nikke-logo";
        logo.src = "image/logo_nikke.png";
        logo.style.position = "absolute";
        logo.style.top = "50%";
        logo.style.left = "50%";
        logo.style.transform = "translate(-50%, -50%)";
        logo.style.zIndex = "-1";
        logo.style.pointerEvents = "none";
        logo.style.opacity = "1";
        document.body.appendChild(logo);
    }
}

// Função para atualizar a câmera
function customCameraUpdate(player) {
    if (typeof player.nrb_zoom !== 'undefined') {
        player.sceneRenderer.camera.zoom = player.nrb_zoom;
    }
    if (typeof player.anrb_posxa !== 'undefined') {
        player.sceneRenderer.camera.position.x += (player.anrb_posxa * 10);
    }
    if (typeof player.nrb_posy !== 'undefined') {
        player.sceneRenderer.camera.position.y += (player.nrb_posy * 10);
    }
}

// Função para reproduzir uma animação
function playAnimation(animation, { next = null, hold = 0, lockTime = 0 } = {}) {
    if (!reproductor) return;

    clearTimeout(animationTimeout);
    clearTimeout(lockTimeout);

    if (hold > 0) {
        reproductor.animationState.setAnimation(0, animation, true);
        if (next) animationTimeout = setTimeout(() => reproductor.animationState.setAnimation(0, next, true), hold);
    } else {
        reproductor.animationState.setAnimation(0, animation, false);
        if (next) reproductor.animationState.addAnimation(0, next, true, 0);
    }

    if (lockTime > 0) {
        animationLocked = true;
        lockTimeout = setTimeout(() => animationLocked = false, lockTime);
    }
}

// Função para reproduzir animações padrão
function playDefaultAnimations() {
    const idle = modelManager.getAnimation("idle") || "idle";
    const action = modelManager.getAnimation("action");
    const hit = modelManager.getAnimation("hit");

    const skeletonData = reproductor.skeleton.data;

    if (clickCount >= 3) {
        clickCount = 0;
        const animToPlay = (hit && skeletonData.findAnimation(hit)) ? hit : idle;
        playAnimation(animToPlay, { next: idle, hold: 5000, lockTime: 3000 });

    } else {
        clickCount++;

        let animToPlay = idle;

        if (action && skeletonData.findAnimation(action)) {
            animToPlay = action;
        }
        else {
            if (skeletonData.findAnimation("serious")) animToPlay = "serious";
            else if (skeletonData.findAnimation("angry")) animToPlay = "angry";
            else if (skeletonData.findAnimation("sad")) animToPlay = "sad";
            else if (skeletonData.findAnimation("expression_0")) animToPlay = "expression_0";
        }

        playAnimation(animToPlay, { next: idle, lockTime: 1500 });
    }
}

// Função para reproduzir animações do modelo cover
function playCoverAnimations() {
    const idle = modelManager.getAnimation("idle");
    const action = modelManager.getAnimation("action");
    const hit = modelManager.getAnimation("hit");
    if (clickCount >= 3) { clickCount = 0; playAnimation(hit, { next: idle, hold: 3000, lockTime: 3000 }); } else playAnimation(action, { next: idle, lockTime: 600 });
}

// Função para reproduzir animações do modelo aim
function playAimAnimations() {
    const idle = modelManager.getAnimation("idle") || "idle";
    const action = modelManager.getAnimation("action");
    const skeletonData = reproductor.skeleton.data;

    if (action && skeletonData.findAnimation(action))
        playAnimation(action, { next: idle });
    else
        playAnimation(idle);
}

// Eventos de clique
function onCanvasClick() {
    if (animationLocked || !reproductor)
        return;

    switch (modelManager.getCurrentVariantId()) {
        case "default": playDefaultAnimations(); break;
        case "cover": playCoverAnimations(); break;
    }
    clearTimeout(clickTimeout); clickTimeout = setTimeout(() => { clickCount = 0; }, 12000);
}

function onMouseDown() {
    if (modelManager.getCurrentVariantId() !== "aim") return;

    playAimAnimations();

    const currentModel = modelManager.getCurrentConfig();
    if (currentModel) {
        soundManager.playShootSound(currentModel.id, currentModel.weapon);
    }
}

// Função para registrar eventos
function registerEvents() {
    canvas.addEventListener("click", onCanvasClick);
    canvas.addEventListener("mousedown", onMouseDown);
}

// Função para o auto player sequencial
function startSequentialAutoplay(minutes) {
    clearInterval(autoplayTimer); autoplayTimer = setInterval(async () => {
        await modelManager.nextModel();
        updateSpinePlayer();
    }, minutes * 60000);
}

// Função para desativar auto play
function stopAutoplay() {
    clearInterval(autoplayTimer); autoplayTimer = null;
}

// Função para o auto player aleatório 
function startRandomAutoplay(minutes) {
    clearInterval(autoplayTimer);
    autoplayTimer = setInterval(async () => {
        await modelManager.loadRandomModel();
        updateSpinePlayer();
    }, minutes * 60000);
}

// Salva o ID do modelo atual no armazenamento do navegador quando o autoplay estiver ativado
function saveCurrentModel(modelId) {
    if (modelId) {
        localStorage.setItem("nikke_last_selected_model", modelId);
    }
}

// Variáveis de controle de fila
let initialProperties = null; // Propriedades iniciais enviadas pelo Wallpaper Engine
let _initReady = false;

// Listener de propriedades do wallpaper
window.wallpaperPropertyListener = {
    applyUserProperties: async function (properties) {
        if (!initialized) {
            initialProperties = properties;
        } else {
            await applyProperties(properties);
        }
    },

    // Captura as propriedades gerais do Wallpaper Engine (como volume mestre)
    applyGeneralProperties: function (properties) {
        if (properties.volume && typeof properties.volume !== "undefined") {
            // O volume do Wallpaper Engine vem de 0 a 100, convertemos para escala de 0.0 a 1.0
            const volumeFraction = properties.volume / 100;
            soundManager.setVolume(volumeFraction);
        }
    }
};

// Função para aplicar as propriedades recebidas do Wallpaper Engine
async function applyProperties(properties) {

    // 1. Atualiza as variáveis globais se as propriedades foram enviadas
    if (properties.autoplay) autoplayEnabled = properties.autoplay.value;

    if (properties.autoplaymode) autoplayMode = properties.autoplaymode.value;

    if (properties.autoplaytime) autoplayTime = properties.autoplaytime.value;
    // Busca o modelo que foi salvo no localStorage
    const savedModelId = localStorage.getItem("nikke_last_selected_model");

    // Para o timer atual para podermos reconfigurar de forma limpa
    stopAutoplay();

    // 2. SE O AUTOPLAY ESTIVER LIGADO
    if (autoplayEnabled) {
        // Dá prioridade ao modelo salvo na memória do PC; se não houver, usa o do menu do WE
        const modelToLoad = savedModelId || (properties.model ? properties.model.value : null);

        if (modelToLoad) {
            await modelManager.loadModel(modelToLoad);
        }

        // Inicia o timer com base no modo selecionado
        if (autoplayMode === "sequential")
            startSequentialAutoplay(autoplayTime);
        else
            startRandomAutoplay(autoplayTime);

    }
    // 3. SE O AUTOPLAY ESTIVER DESLIGADO (Modo Manual)
    else {
        // Se o usuário trocou o modelo direto pelo menu do Wallpaper Engine, carrega ele
        if (properties.model && properties.model.value) {
            await modelManager.loadModel(properties.model.value);
        }
    }

    // Garante que o Spine seja atualizado e renderizado
    await updateSpinePlayer();

    // 4. Atualiza a visibilidade dos botões de navegação
    if (properties.showmodelcontrols && typeof properties.showmodelcontrols.value !== "undefined") {
        toggleModelNavButtons(properties.showmodelcontrols.value);
    }
}

// Função para exibir ou ocultar os botões de avançar e voltar modelo
// Atualiza o texto da caixa com o nome do modelo atual
function updateModelNavLabel() {
    const label = document.getElementById("model-nav-label");
    if (!label)
        return;

    // Busca o nome no config ou usa o ID como fallback

    label.innerText = modelManager.getCurrentModelName();
}

// Cria os estilos globais de hover para os botões uma única vez
const styleSheet = document.createElement("style");
styleSheet.innerText = `
    .nav-btn {
        background-color: rgba(255, 255, 255, 0.3);
        transition: background-color 0.2s, transform 0.1s;
    }
    .nav-btn:hover {
        background-color: rgba(255, 255, 255, 0.5) !important;
    }
`;
document.head.appendChild(styleSheet);

// Cria/Exibe os botões com a etiqueta do nome
function toggleModelNavButtons(show) {
    const containerId = "model-nav-container";
    let container = document.getElementById(containerId);

    if (!show) {
        container?.remove();
        return;
    }

    if (!container) {
        container = document.createElement("div");
        container.id = containerId;
        container.style.cssText = `
            position: absolute;
            right: 15px;
            top: 15px;
            display: flex;
            align-items: center;
            gap: 10px;
            z-index: 10;
            background-color: rgba(255, 255, 255, 0.3);
            padding: 5px;
            border-radius: 30px;
        `;

        // Removemos o background e a transition daqui, pois agora a classe .nav-btn cuida disso!
        const buttonStyle = `
            width: 40px;
            height: 40px;
            border: none;
            border-radius: 50%;
            color: #ffffff;
            font-size: 18px;
            font-weight: bold;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            user-select: none;
        `;

        // Botão Voltar ( < )
        const btnPrev = document.createElement("button");
        btnPrev.className = "nav-btn"; // <--- Aplica o CSS
        btnPrev.innerHTML = "&#10094;";
        btnPrev.style.cssText = buttonStyle;
        btnPrev.onclick = async (e) => {
            e.stopPropagation();
            if (typeof modelManager.prevModel === "function") await modelManager.prevModel();
            else if (typeof modelManager.previousModel === "function") await modelManager.previousModel();
            await updateSpinePlayer();
        };

        // Etiqueta com o Nome do Personagem
        const label = document.createElement("span");
        label.id = "model-nav-label";
        label.style.cssText = `
            padding: 8px 12px;
            border-radius: 20px;
            color: #ffffff;
            font-family: Arial, sans-serif;
            font-size: 12px;
            font-weight: bold;
            white-space: nowrap;
            user-select: none;
            min-width: 80px;
            max-width: 80px;
            display: flex;
            align-items: center;
            justify-content: center;
            text-align: center;
            overflow: hidden;
            -webkit-mask-image: linear-gradient(to right, transparent 0%, #000 15%, #000 85%, transparent 100%);
            mask-image: linear-gradient(to right, transparent 0%, #000 15%, #000 85%, transparent 100%);
        `;

        // Botão Avançar ( > )
        const btnNext = document.createElement("button"); // <-- Corrigido para btnNext
        btnNext.className = "nav-btn"; // <--- Aplica o CSS
        btnNext.innerHTML = "&#10095;"; // <-- Corrigido para a seta direita
        btnNext.style.cssText = buttonStyle;
        btnNext.onclick = async (e) => { // <-- Restaurada a função de clique
            e.stopPropagation();
            await modelManager.nextModel();
            await updateSpinePlayer();
        };

        // Adiciona tudo no container
        container.appendChild(btnPrev);
        container.appendChild(label);
        container.appendChild(btnNext);
        document.body.appendChild(container);
    }

    // Garante que o texto atualize sempre que a função for chamada
    updateModelNavLabel();
}

// Inicialização assíncrona da aplicação
init();