export default class SoundManager {
    constructor() {
        this.soundsDatabase = null;
        this.soundPath = "sounds/";
        this.audioCtx = null;
        this.audioBuffers = {}; // Cache para guardar os sons decodificados na memória RAM
        this.masterVolume = 0.5; // Volume padrão inicial (de 0.0 a 1.0)
        this.gainNode = null;
    }

    /**
     * Carrega o banco de dados de sons uma única vez
     */
    async init() {
        try {
            const response = await fetch(`${this.soundPath}soundList.json`);
            this.soundsDatabase = await response.json();
            console.log("🔊 Banco de sons carregado com sucesso!");
            
            // Tenta inicializar o contexto de áudio de forma silenciosa
            this.initAudioContext();
        } catch (error) {
            console.error("❌ Erro ao carregar o banco de sons:", error);
        }
    }

    /**
     * Inicializa o contexto de áudio da Web Audio API
     */
    initAudioContext() {
        if (this.audioCtx) return;

        const AudioContextClass = window.AudioContext || window.webkitAudioContext;
        if (AudioContextClass) {
            this.audioCtx = new AudioContextClass();
            // Cria um nó de ganho (controle de volume geral)
            this.gainNode = this.audioCtx.createGain();
            this.gainNode.gain.setValueAtTime(this.masterVolume, this.audioCtx.currentTime);
            this.gainNode.connect(this.audioCtx.destination);
        }
    }

    /**
     * Define o volume mestre (integrado com o Wallpaper Engine)
     * @param {number} val - Volume de 0.0 a 1.0
     */
    setVolume(val) {
        this.masterVolume = Math.max(0, Math.min(1, val));
        if (this.gainNode && this.audioCtx) {
            this.gainNode.gain.setValueAtTime(this.masterVolume, this.audioCtx.currentTime);
        }
    }

    /**
     * Carrega e decodifica o arquivo de áudio sob demanda, guardando-o no cache de memória
     */
    async getAudioBuffer(soundFile) {
        if (this.audioBuffers[soundFile]) {
            return this.audioBuffers[soundFile];
        }

        try {
            const response = await fetch(`${this.soundPath}${soundFile}`);
            const arrayBuffer = await response.arrayBuffer();
            
            this.initAudioContext();
            if (!this.audioCtx) return null;

            // Decodifica os dados binários do áudio em PCM bruto na memória RAM (latência zero ao reproduzir)
            const audioBuffer = await this.audioCtx.decodeAudioData(arrayBuffer);
            this.audioBuffers[soundFile] = audioBuffer;
            return audioBuffer;
        } catch (e) {
            console.error(`❌ Erro ao decodificar o arquivo de som ${soundFile}:`, e);
            return null;
        }
    }

    /**
     * Toca o som de forma instantânea e otimizada para o Wallpaper Engine
     */
    async playShootSound(modelId, weapon) {
        if (!this.soundsDatabase) {
            console.warn("⚠️ Banco de sons não carregado ainda.");
            return;
        }

        let soundFile = null;

        // 1. Verifica se o personagem tem som exclusivo
        if (this.soundsDatabase.especial && this.soundsDatabase.especial[modelId]) {
            soundFile = this.soundsDatabase.especial[modelId][0];
        } 
        // 2. Se não tiver, usa o genérico do tipo de arma
        else if (this.soundsDatabase.generic && this.soundsDatabase.generic[weapon]) {
            soundFile = this.soundsDatabase.generic[weapon];
        }

        if (!soundFile) {
            console.warn(`🤷 Nenhum som configurado para o ID "${modelId}" ou Arma "${weapon}".`);
            return;
        }

        // Garante que o contexto de áudio seja ativado (bypassa restrições de autoplay do WE)
        this.initAudioContext();
        if (this.audioCtx && this.audioCtx.state === "suspended") {
            await this.audioCtx.resume();
        }

        try {
            const buffer = await this.getAudioBuffer(soundFile);
            if (buffer && this.audioCtx) {
                // Cria uma "fonte de áudio" virtual super leve
                const source = this.audioCtx.createBufferSource();
                source.buffer = buffer;

                // Conecta a fonte ao controle de volume e depois às caixas de som
                source.connect(this.gainNode);
                
                // Dispara o som instantaneamente
                source.start(0);
                console.log(`🔥 Disparo! Arma: ${weapon} | Arquivo: ${soundFile} (Web Audio API)`);
            }
        } catch (error) {
            console.error("Erro ao reproduzir som com Web Audio API:", error);
        }
    }
}