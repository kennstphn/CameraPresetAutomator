// create eel functions here
eel.expose(push_render_data);

function push_render_data(data) {
    Vue.prototype.$eel.app = data
}

eel.expose(log_data)

function log_data(info) {
    Vue.prototype.$eel.log_data = info
}

Vue.prototype.$eel = new Vue({
    data: {
        app: null,
        log_data: null,
        show_application_data: false,
        arm_preset_storage: false,
        arm_capture:false,
        darkMode:true,
        loading_presets:false,
        capturedPositions:[
            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
            [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]],
        ]
    },
    methods: {
        recall_camera_list: function (i) {
            return eel.recall_camera_list(i)
        },
        recall_camera: function (camera_number, i) {
            eel.recall_camera(camera_number, i)
        },
        store_current_position_as_preset: function (i,callable) {
            return eel.store_current_position_as_preset(i)(callable)
        },
        arm(str){
            if(str === 'capture'){
                this.arm_preset_storage = false;
                this.arm_capture = true;
            }else if(str === 'store'){
                this.arm_preset_storage = true;
                this.arm_capture = false;
            }else{
                this.arm_preset_storage = false;
                this.arm_capture = false;
            }
        },
        capture:function(i){
            Vue.set(this.capturedPositions[0],i,this.app.camera1.position)
            Vue.set(this.capturedPositions[1],i,this.app.camera2.position)
            Vue.set(this.capturedPositions[2],i,this.app.camera3.position)
            Vue.set(this.capturedPositions[3],i,this.app.camera4.position)
            Vue.set(this.capturedPositions[4],i,this.app.camera5.position)
        },
    },
    watch: {},
    computed: {
        recalling: function () {
            return (this.$eel.app.camera1.attempted_preset === this.number || this.$eel.app.camera1.connected === false) &&
                (this.$eel.app.camera2.attempted_preset === this.number || this.$eel.app.camera2.connected === false) &&
                (this.$eel.app.camera3.attempted_preset === this.number || this.$eel.app.camera3.connected === false) &&
                (this.$eel.app.camera4.attempted_preset === this.number || this.$eel.app.camera4.connected === false) &&
                (this.$eel.app.camera5.attempted_preset === this.number || this.$eel.app.camera5.connected === false) &&
                (
                    this.$eel.app.camera1.preset !== this.number ||
                    this.$eel.app.camera2.preset !== this.number ||
                    this.$eel.app.camera3.preset !== this.number ||
                    this.$eel.app.camera4.preset !== this.number ||
                    this.$eel.app.camera5.preset !== this.number
                )
        }
    }
})