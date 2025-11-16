// frontend/src/extensions/tiptapExtensions.ts

import { Extension } from '@tiptap/core';
import '@tiptap/extension-text-style'; // Importar para modificar

// Declarar os tipos para o Tiptap
declare module '@tiptap/core' {
  interface Commands<ReturnType> {
    fontSize: {
      /**
       * Define o tamanho da fonte.
       */
      setFontSize: (size: string) => ReturnType;
      /**
       * Remove o tamanho da fonte.
       */
      unsetFontSize: () => ReturnType;
    };
  }
}

/**
 * Esta é uma extensão Tiptap customizada que ADICIONA o atributo `fontSize`
 * à marca `textStyle` existente (que já é usada por FontFamily e Color).
 */
export const FontSize = Extension.create({
  name: 'fontSize', // Nome da extensão

  addOptions() {
    return {
      types: ['textStyle'], // O nome da marca que queremos estender
    };
  },

  // Adiciona o atributo 'fontSize' globalmente aos tipos em 'this.options.types'
  addGlobalAttributes() {
    return [
      {
        types: this.options.types,
        attributes: {
          fontSize: {
            default: null,
            // Define como ler o atributo do HTML (ex: <span style="font-size: 16px;">)
            parseHTML: (element) => element.style.fontSize,
            // Define como escrever o atributo no HTML
            renderHTML: (attributes) => {
              if (!attributes.fontSize) {
                return {};
              }
              return { style: `font-size: ${attributes.fontSize}` };
            },
          },
        },
      },
    ];
  },

  // Adiciona os comandos `setFontSize` e `unsetFontSize`
  addCommands() {
    return {
      setFontSize: (fontSize: string) => ({ chain }) => {
        return chain().setMark('textStyle', { fontSize }).run();
      },
      unsetFontSize: () => ({ chain }) => {
        // Remove o atributo 'fontSize' mantendo outros estilos (como cor)
        return chain().setMark('textStyle', { fontSize: null }).run();
      },
    };
  },
});