var honeypot = new Vue({
    el: '#honeypot',
    data: {
        message: 'testing stuff'
    },
    methods: {
        SourceIPButton: function(){
            this.message = this.message.split('').reverse().join('')
        }
    }
})