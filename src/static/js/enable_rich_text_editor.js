(function ($) {
    'use strict';

    $(document).ready(function () {

        $('textarea.textarea-wysiwyg').trumbowyg({
            lang: 'fr',
            btns: [
                ['viewHTML'],
                ['undo', 'redo'],
                ['formatting'],
                ['strong', 'em'],
                ['link'],
                ['unorderedList', 'orderedList'],
                ['removeformat'],
                ['fullscreen']
            ],
            minimalLinks: true,
            removeformatPasted: true,
        });
    });
}($ || django.jQuery));
