<template>
  <div class="offer-letter-editor border rounded bg-white">
    <!-- Toolbar -->
    <div ref="toolbar" class="quill-toolbar border-bottom bg-light">
      <span class="ql-formats">
        <select class="ql-header">
          <option value="1"></option>
          <option value="2"></option>
          <option value="3"></option>
          <option selected></option>
        </select>
        <select class="ql-font"></select>
      </span>
      <span class="ql-formats">
        <button class="ql-bold"></button>
        <button class="ql-italic"></button>
        <button class="ql-underline"></button>
        <button class="ql-strike"></button>
      </span>
      <span class="ql-formats">
        <button class="ql-list" value="ordered"></button>
        <button class="ql-list" value="bullet"></button>
        <select class="ql-align"></select>
      </span>
      <span class="ql-formats">
        <button class="ql-link"></button>
        <button class="ql-image"></button>
      </span>
      <span class="ql-formats ms-auto">
        <select class="form-select form-select-sm d-inline-block w-auto ms-2" @change="insertVariable($event)">
          <option value="">Insert Variable...</option>
          <option value="{{ student_name }}">Student Name</option>
          <option value="{{ company_name }}">Company Name</option>
          <option value="{{ company_location }}">Company Location</option>
          <option value="{{ company_hr_name }}">HR Name</option>
          <option value="{{ today_date }}">Today's Date</option>
          <option value="{{ joining_date }}">Joining Date</option>
          <option value="{{ placement.position }}">Job Role</option>
          <option value="{{ placement.salary }}">Salary/Package</option>
          <option value="<br/><br/><img src='{{ company_signature }}' style='max-height:60px;'/><br/>">Company Signature</option>
        </select>
      </span>
    </div>

    <!-- Editor Container -->
    <div ref="editor" class="quill-editor" style="min-height: 400px;"></div>
  </div>
</template>

<script>
import { ref, onMounted, onBeforeUnmount, watch } from 'vue';

export default {
  name: 'OfferLetterEditor',
  props: {
    modelValue: {
      type: String,
      default: ''
    }
  },
  emits: ['update:modelValue'],
  setup(props, { emit }) {
    const editor = ref(null);
    const toolbar = ref(null);
    let quill = null;
    let isUpdating = false;

    const loadQuill = () => {
      return new Promise((resolve) => {
        if (window.Quill) {
          resolve(window.Quill);
          return;
        }
        
        // Load Quill CSS
        if (!document.getElementById('quill-css')) {
          const link = document.createElement('link');
          link.id = 'quill-css';
          link.rel = 'stylesheet';
          link.href = 'https://cdn.quilljs.com/1.3.6/quill.snow.css';
          document.head.appendChild(link);
        }

        // Load Quill JS
        const script = document.createElement('script');
        script.src = 'https://cdn.quilljs.com/1.3.6/quill.js';
        script.onload = () => resolve(window.Quill);
        document.head.appendChild(script);
      });
    };

    onMounted(async () => {
      const Quill = await loadQuill();
      
      quill = new Quill(editor.value, {
        theme: 'snow',
        modules: {
          toolbar: toolbar.value
        },
        placeholder: 'Design your offer letter template here... Use the variables dropdown to insert dynamic data.'
      });

      if (props.modelValue) {
        quill.clipboard.dangerouslyPasteHTML(props.modelValue);
      }

      quill.on('text-change', () => {
        isUpdating = true;
        emit('update:modelValue', quill.root.innerHTML);
        setTimeout(() => { isUpdating = false; }, 0);
      });
    });

    watch(() => props.modelValue, (newVal) => {
      if (quill && !isUpdating) {
        const currentHtml = quill.root.innerHTML;
        if (newVal !== currentHtml) {
          quill.clipboard.dangerouslyPasteHTML(newVal || '');
        }
      }
    });

    const insertVariable = (event) => {
      const val = event.target.value;
      if (val && quill) {
        const range = quill.getSelection(true);
        if (val.includes('<img')) {
           quill.clipboard.dangerouslyPasteHTML(range.index, val);
        } else {
           quill.insertText(range.index, val);
        }
        event.target.value = ""; // reset dropdown
      }
    };

    return { editor, toolbar, insertVariable };
  }
}
</script>

<style scoped>
.offer-letter-editor {
  display: flex;
  flex-direction: column;
}
.quill-toolbar {
  border-top: none;
  border-left: none;
  border-right: none;
  border-radius: var(--ppa-radius) var(--ppa-radius) 0 0;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  padding: 0.5rem;
}
.quill-editor {
  font-family: inherit;
  font-size: 1rem;
  border: none !important;
}
.ql-container.ql-snow {
  border: none;
}
</style>
