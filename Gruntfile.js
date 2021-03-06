/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

path = require('path');

module.exports = function (grunt) {

    // Project configuration.
    grunt.initConfig({
        pkg: grunt.file.readJSON('package.json'),
        jshint: {
            options: {
                jshintrc: true
            },
            development: ['media/js/**/*.js']
        },
        less: {
            development: {
                options: {
                    paths: ['media/css/']
                },
                files: {
                    'media/css/**/*.css': 'media/css/**/*.less'
                }
            }
        },
        watch: {
            options: {
                port: 35729,
                livereload: true,
                nospawn: true
            },
            css: {
                files: ['media/css/**/*.less'],
                tasks: ['less']
            },
            scripts: {
                files: ['media/js/**/*.js'],
                tasks: ['jshint']
            },
            html: {
                files: ['bedrock/**/*.html']
            }
        }
    });

    // Update the config to only build the changed files.
    grunt.event.on('watch', function (action, filepath) {
        grunt.config(['less', 'development', 'files'], [
            { src: filepath, dest: filepath + '.css' }
        ]);

        grunt.config(['jshint', 'development'], [filepath]);
    });

    grunt.loadNpmTasks('grunt-contrib-less');
    grunt.loadNpmTasks('grunt-contrib-jshint');
    grunt.loadNpmTasks('grunt-contrib-watch');

    // Default task(s).
    grunt.registerTask('default', ['watch']);

};
