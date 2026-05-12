        document.addEventListener('DOMContentLoaded', function () {
            if (typeof ClassicEditor === 'undefined') {
                console.warn('CKEditor could not be loaded. Using textarea fallback.');
                var ta = document.getElementById('postContent');
                if (ta) { ta.style.display = ''; ta.style.width = '100%'; ta.style.minHeight = '200px'; ta.rows = 8; ta.required = true; ta.placeholder = 'Write your post content here...'; ta.style.padding = '12px 15px'; ta.style.border = '2px solid #d0d7de'; ta.style.borderRadius = '8px'; ta.style.fontSize = '14px'; ta.style.resize = 'vertical'; ta.style.boxSizing = 'border-box'; }
                return;
            }

            // Define custom Base64 upload adapter natively for ckeditor
            class Base64UploadAdapter {
                constructor(loader) { this.loader = loader; }
                upload() {
                    return this.loader.file.then(file => new Promise((resolve, reject) => {
                        const reader = new FileReader();
                        reader.onload = function () {
                            // Compress and scale down to a max width/height of 700px before resolving
                            if (typeof compressImage === 'function') {
                                compressImage(reader.result, 700, 700, function (compressedSrc) {
                                    resolve({ default: compressedSrc });
                                });
                            } else {
                                resolve({ default: reader.result });
                            }
                        };
                        reader.onerror = function (error) { reject(error); };
                        reader.readAsDataURL(file);
                    }));
                }
                abort() { }
            }
            function MyCustomUploadAdapterPlugin(editor) {
                editor.plugins.get('FileRepository').createUploadAdapter = (loader) => {
                    return new Base64UploadAdapter(loader);
                };
            }

            ClassicEditor.create(document.getElementById('postContentEditor'), {
                toolbar: { items: ['heading', '|', 'bold', 'italic', 'underline', 'strikethrough', '|', 'bulletedList', 'numberedList', '|', 'outdent', 'indent', '|', 'blockQuote', 'insertTable', '|', 'uploadImage', 'link', '|', 'undo', 'redo'] },
                placeholder: 'Write your post content here...',
                extraPlugins: [MyCustomUploadAdapterPlugin],
                ui: { viewportOffset: { top: 80 } },
                image: {
                    resizeUnit: '%',
                    resizeOptions: [
                        { name: 'resizeImage:original', value: null, label: 'Original' },
                        { name: 'resizeImage:25', value: '25', label: '25%' },
                        { name: 'resizeImage:50', value: '50', label: '50%' },
                        { name: 'resizeImage:75', value: '75', label: '75%' }
                    ],
                    toolbar: [
                        'imageStyle:inline', 'imageStyle:block', 'imageStyle:side',
                        '|',
                        'toggleImageCaption', 'imageTextAlternative',
                        '|',
                        'resizeImage'
                    ]
                }
            }).then(function (editor) {
                window._postEditor = editor;
                editor.model.document.on('change:data', function () {
                    var ta = document.getElementById('postContent');
                    if (ta) ta.value = editor.getData();
                });
                console.log('CKEditor 5 ready for Post modal.');

                // Double-click listener for cropping existing images
                const editableElement = editor.ui.view.editable.element;
                if (editableElement) {
                    editableElement.addEventListener('dblclick', function (e) {
                        if (e.target && e.target.tagName === 'IMG') {
                            e.preventDefault();
                            const imgSrc = e.target.getAttribute('src');
                            if (imgSrc) {
                                if (typeof openCropperModal === 'function') {
                                    openCropperModal(imgSrc, function (result) {
                                        const newSrc = result.default || result;
                                        const selectedElement = editor.model.document.selection.getSelectedElement();
                                        if (selectedElement && (selectedElement.is('element', 'imageBlock') || selectedElement.is('element', 'imageInline') || selectedElement.name === 'imageBlock' || selectedElement.name === 'imageInline')) {
                                            editor.model.change(writer => {
                                                writer.setAttribute('src', newSrc, selectedElement);
                                            });
                                            console.log('Applied crop natively to CKEditor model!');
                                        } else {
                                            console.warn('Image not selected in CKEditor model, updating DOM directly.');
                                            e.target.src = newSrc;
                                            editor.updateSourceElement();
                                        }
                                    }, function (err) {
                                        console.log(err);
                                    });
                                }
                            }
                        }
                    });
                }

            }).catch(function (err) {
                console.error('CKEditor init error:', err);
                var ta = document.getElementById('postContent');
                if (ta) { ta.style.display = ''; ta.style.width = '100%'; ta.style.minHeight = '200px'; ta.rows = 8; }
            });

            // Initialize Calendar Description CKEditor
            ClassicEditor.create(document.getElementById('calendarContentEditor'), {
                toolbar: { items: ['heading', '|', 'bold', 'italic', 'underline', 'strikethrough', '|', 'bulletedList', 'numberedList', '|', 'outdent', 'indent', '|', 'blockQuote', 'insertTable', '|', 'uploadImage', 'link', '|', 'undo', 'redo'] },
                placeholder: 'Describe the academic calendar...',
                extraPlugins: [MyCustomUploadAdapterPlugin],
                ui: { viewportOffset: { top: 80 } },
                image: {
                    resizeUnit: '%',
                    resizeOptions: [
                        { name: 'resizeImage:original', value: null, label: 'Original' },
                        { name: 'resizeImage:25', value: '25', label: '25%' },
                        { name: 'resizeImage:50', value: '50', label: '50%' },
                        { name: 'resizeImage:75', value: '75', label: '75%' }
                    ],
                    toolbar: [
                        'imageStyle:inline', 'imageStyle:block', 'imageStyle:side',
                        '|',
                        'toggleImageCaption', 'imageTextAlternative',
                        '|',
                        'resizeImage'
                    ]
                }
            }).then(function (editor) {
                window._calendarEditor = editor;
                editor.model.document.on('change:data', function () {
                    var ta = document.getElementById('calendarDescription');
                    if (ta) ta.value = editor.getData();
                });
                console.log('CKEditor 5 ready for Calendar modal.');

                // Double-click listener for cropping existing calendar images
                const editableElement = editor.ui.view.editable.element;
                if (editableElement) {
                    editableElement.addEventListener('dblclick', function (e) {
                        if (e.target && e.target.tagName === 'IMG') {
                            e.preventDefault();
                            const imgSrc = e.target.getAttribute('src');
                            if (imgSrc) {
                                if (typeof openCropperModal === 'function') {
                                    openCropperModal(imgSrc, function (result) {
                                        const newSrc = result.default || result;
                                        const selectedElement = editor.model.document.selection.getSelectedElement();
                                        if (selectedElement && (selectedElement.is('element', 'imageBlock') || selectedElement.is('element', 'imageInline') || selectedElement.name === 'imageBlock' || selectedElement.name === 'imageInline')) {
                                            editor.model.change(writer => {
                                                writer.setAttribute('src', newSrc, selectedElement);
                                            });
                                        } else {
                                            e.target.src = newSrc;
                                            editor.updateSourceElement();
                                        }
                                    }, function (err) {
                                        console.log(err);
                                    });
                                }
                            }
                        }
                    });
                }
            }).catch(function (err) {
                console.error('CKEditor (Calendar) init error:', err);
                var ta = document.getElementById('calendarDescription');
                if (ta) { ta.style.display = ''; ta.style.width = '100%'; ta.style.minHeight = '200px'; ta.rows = 8; }
            });

            // Initialize Alumni News CKEditor
            ClassicEditor.create(document.getElementById('alumniNewsContentEditor'), {
                toolbar: { items: ['heading', '|', 'bold', 'italic', 'underline', 'strikethrough', '|', 'bulletedList', 'numberedList', '|', 'outdent', 'indent', '|', 'blockQuote', 'insertTable', '|', 'uploadImage', 'link', '|', 'undo', 'redo'] },
                placeholder: 'Write news content...',
                extraPlugins: [MyCustomUploadAdapterPlugin],
                ui: { viewportOffset: { top: 80 } },
                image: {
                    resizeUnit: '%',
                    resizeOptions: [
                        { name: 'resizeImage:original', value: null, label: 'Original' },
                        { name: 'resizeImage:25', value: '25', label: '25%' },
                        { name: 'resizeImage:50', value: '50', label: '50%' },
                        { name: 'resizeImage:75', value: '75', label: '75%' }
                    ],
                    toolbar: [
                        'imageStyle:inline', 'imageStyle:block', 'imageStyle:side',
                        '|',
                        'toggleImageCaption', 'imageTextAlternative',
                        '|',
                        'resizeImage'
                    ]
                }
            }).then(function (editor) {
                window._alumniNewsEditor = editor;
                editor.model.document.on('change:data', function () {
                    var ta = document.getElementById('alumniNewsContent');
                    if (ta) ta.value = editor.getData();
                });
                console.log('CKEditor 5 ready for Alumni News modal.');

                // Double-click listener for cropping existing images
                const editableElement = editor.ui.view.editable.element;
                if (editableElement) {
                    editableElement.addEventListener('dblclick', function (e) {
                        if (e.target && e.target.tagName === 'IMG') {
                            e.preventDefault();
                            const imgSrc = e.target.getAttribute('src');
                            if (imgSrc) {
                                if (typeof openCropperModal === 'function') {
                                    openCropperModal(imgSrc, function (result) {
                                        const newSrc = result.default || result;
                                        const selectedElement = editor.model.document.selection.getSelectedElement();
                                        if (selectedElement && (selectedElement.is('element', 'imageBlock') || selectedElement.is('element', 'imageInline') || selectedElement.name === 'imageBlock' || selectedElement.name === 'imageInline')) {
                                            editor.model.change(writer => {
                                                writer.setAttribute('src', newSrc, selectedElement);
                                            });
                                        } else {
                                            e.target.src = newSrc;
                                            editor.updateSourceElement();
                                        }
                                    }, function (err) {
                                        console.log(err);
                                    });
                                }
                            }
                        }
                    });
                }
            }).catch(function (err) {
                console.error('CKEditor (Alumni News) init error:', err);
                var ta = document.getElementById('alumniNewsContent');
                if (ta) { ta.style.display = ''; ta.style.width = '100%'; ta.style.minHeight = '300px'; ta.rows = 5; }
            });

            // Initialize Alumni Event Description CKEditor
            ClassicEditor.create(document.getElementById('alumniEventDescriptionEditor'), {
                toolbar: { items: ['heading', '|', 'bold', 'italic', 'underline', 'strikethrough', '|', 'bulletedList', 'numberedList', '|', 'outdent', 'indent', '|', 'blockQuote', 'insertTable', '|', 'uploadImage', 'link', '|', 'undo', 'redo'] },
                placeholder: 'Describe the event...',
                extraPlugins: [MyCustomUploadAdapterPlugin],
                ui: { viewportOffset: { top: 80 } },
                image: {
                    resizeUnit: '%',
                    resizeOptions: [
                        { name: 'resizeImage:original', value: null, label: 'Original' },
                        { name: 'resizeImage:25', value: '25', label: '25%' },
                        { name: 'resizeImage:50', value: '50', label: '50%' },
                        { name: 'resizeImage:75', value: '75', label: '75%' }
                    ],
                    toolbar: [
                        'imageStyle:inline', 'imageStyle:block', 'imageStyle:side',
                        '|',
                        'toggleImageCaption', 'imageTextAlternative',
                        '|',
                        'resizeImage'
                    ]
                }
            }).then(function (editor) {
                window.alumniEventEditor = editor;
                editor.model.document.on('change:data', function () {
                    var ta = document.getElementById('alumniEventDescription');
                    if (ta) ta.value = editor.getData();
                });
                console.log('CKEditor 5 ready for Alumni Event modal.');
            }).catch(function (err) {
                console.error('CKEditor (Alumni Event) init error:', err);
                var ta = document.getElementById('alumniEventDescription');
                if (ta) { ta.style.display = ''; ta.style.width = '100%'; ta.style.minHeight = '260px'; ta.rows = 5; }
            });


            // Initialize Success Story CKEditor
            ClassicEditor.create(document.getElementById('storyContentEditor'), {
                toolbar: { items: ['heading', '|', 'bold', 'italic', 'underline', 'strikethrough', '|', 'bulletedList', 'numberedList', '|', 'outdent', 'indent', '|', 'blockQuote', 'insertTable', '|', 'uploadImage', 'link', '|', 'undo', 'redo'] },
                placeholder: 'Describe their success story...',
                extraPlugins: [MyCustomUploadAdapterPlugin],
                ui: { viewportOffset: { top: 80 } },
                image: {
                    resizeUnit: '%',
                    resizeOptions: [
                        { name: 'resizeImage:original', value: null, label: 'Original' },
                        { name: 'resizeImage:25', value: '25', label: '25%' },
                        { name: 'resizeImage:50', value: '50', label: '50%' },
                        { name: 'resizeImage:75', value: '75', label: '75%' }
                    ],
                    toolbar: [
                        'imageStyle:inline', 'imageStyle:block', 'imageStyle:side',
                        '|',
                        'toggleImageCaption', 'imageTextAlternative',
                        '|',
                        'resizeImage'
                    ]
                }
            }).then(function (editor) {
                window._storyEditor = editor;
                editor.model.document.on('change:data', function () {
                    var ta = document.getElementById('storyDescription');
                    if (ta) ta.value = editor.getData();
                });
                console.log('CKEditor 5 ready for Success Story modal.');

                // Double-click listener for cropping existing images
                const editableElement = editor.ui.view.editable.element;
                if (editableElement) {
                    editableElement.addEventListener('dblclick', function (e) {
                        if (e.target && e.target.tagName === 'IMG') {
                            e.preventDefault();
                            const imgSrc = e.target.getAttribute('src');
                            if (imgSrc) {
                                if (typeof openCropperModal === 'function') {
                                    openCropperModal(imgSrc, function (result) {
                                        const newSrc = result.default || result;
                                        const selectedElement = editor.model.document.selection.getSelectedElement();
                                        if (selectedElement && (selectedElement.is('element', 'imageBlock') || selectedElement.is('element', 'imageInline') || selectedElement.name === 'imageBlock' || selectedElement.name === 'imageInline')) {
                                            editor.model.change(writer => {
                                                writer.setAttribute('src', newSrc, selectedElement);
                                            });
                                        } else {
                                            e.target.src = newSrc;
                                            editor.updateSourceElement();
                                        }
                                    }, function (err) {
                                        console.log(err);
                                    });
                                }
                            }
                        }
                    });
                }
            }).catch(function (err) {
                console.error('CKEditor (Success Story) init error:', err);
                var ta = document.getElementById('storyDescription');
                if (ta) { ta.style.display = ''; ta.style.width = '100%'; ta.style.minHeight = '300px'; ta.rows = 5; }
            });

            // Initialize Achievement CKEditor
            ClassicEditor.create(document.getElementById('achievementContentEditor'), {
                toolbar: { items: ['heading', '|', 'bold', 'italic', 'underline', 'strikethrough', '|', 'bulletedList', 'numberedList', '|', 'outdent', 'indent', '|', 'blockQuote', 'insertTable', '|', 'uploadImage', 'link', '|', 'undo', 'redo'] },
                placeholder: 'Describe the achievement...',
                extraPlugins: [MyCustomUploadAdapterPlugin],
                ui: { viewportOffset: { top: 80 } },
                image: {
                    resizeUnit: '%',
                    resizeOptions: [
                        { name: 'resizeImage:original', value: null, label: 'Original' },
                        { name: 'resizeImage:25', value: '25', label: '25%' },
                        { name: 'resizeImage:50', value: '50', label: '50%' },
                        { name: 'resizeImage:75', value: '75', label: '75%' }
                    ],
                    toolbar: [
                        'imageStyle:inline', 'imageStyle:block', 'imageStyle:side',
                        '|',
                        'toggleImageCaption', 'imageTextAlternative',
                        '|',
                        'resizeImage'
                    ]
                }
            }).then(function (editor) {
                window._achievementEditor = editor;
                editor.model.document.on('change:data', function () {
                    var ta = document.getElementById('achievementDescription');
                    if (ta) ta.value = editor.getData();
                });
                console.log('CKEditor 5 ready for Achievement modal.');

                // Double-click listener for cropping existing images
                const editableElement = editor.ui.view.editable.element;
                if (editableElement) {
                    editableElement.addEventListener('dblclick', function (e) {
                        if (e.target && e.target.tagName === 'IMG') {
                            e.preventDefault();
                            const imgSrc = e.target.getAttribute('src');
                            if (imgSrc && typeof openCropperModal === 'function') {
                                openCropperModal(imgSrc, function (result) {
                                    const newSrc = result.default || result;
                                    const selectedElement = editor.model.document.selection.getSelectedElement();
                                    if (selectedElement && (selectedElement.name === 'imageBlock' || selectedElement.name === 'imageInline')) {
                                        editor.model.change(writer => {
                                            writer.setAttribute('src', newSrc, selectedElement);
                                        });
                                    } else {
                                        e.target.src = newSrc;
                                        editor.updateSourceElement();
                                    }
                                }, function (err) { console.log(err); });
                            }
                        }
                    });
                }
            }).catch(function (err) {
                console.error('CKEditor (Achievement) init error:', err);
                var ta = document.getElementById('achievementDescription');
                if (ta) { ta.style.display = ''; ta.style.width = '100%'; ta.style.minHeight = '300px'; ta.rows = 5; }
            });

            // Initialize NORSU Information CKEditors
            const norsuInfoEditors = [
                { id: 'infoGeneralMandate', placeholder: 'Enter general mandate...' },
                { id: 'infoVision', placeholder: 'Enter NORSU vision statement...' },
                { id: 'infoMission', placeholder: 'Enter NORSU mission statement...' },
                { id: 'infoStrategicGoals', placeholder: 'Enter strategic goals...' },
                { id: 'infoCoreValues', placeholder: 'Enter core values...' },
                { id: 'infoQualityPolicy', placeholder: 'Enter quality policy statement...' }
            ];

            norsuInfoEditors.forEach(info => {
                if (document.getElementById(info.id + 'Editor')) {
                    ClassicEditor.create(document.getElementById(info.id + 'Editor'), {
                        toolbar: { items: ['heading', '|', 'bold', 'italic', 'underline', 'strikethrough', '|', 'bulletedList', 'numberedList', '|', 'outdent', 'indent', '|', 'blockQuote', 'insertTable', '|', 'link', '|', 'undo', 'redo'] },
                        placeholder: info.placeholder,
                        ui: { viewportOffset: { top: 80 } }
                    }).then(function (editor) {
                        window['_' + info.id + 'Editor'] = editor;
                        editor.model.document.on('change:data', function () {
                            var ta = document.getElementById(info.id);
                            if (ta) ta.value = editor.getData();
                        });
                        console.log('CKEditor 5 ready for ' + info.id);
                    }).catch(function (err) {
                        console.error('CKEditor (' + info.id + ') init error:', err);
                        var ta = document.getElementById(info.id);
                        if (ta) { ta.style.display = ''; ta.style.width = '100%'; ta.style.minHeight = '120px'; ta.rows = 3; }
                    });
                }
            });

        });
