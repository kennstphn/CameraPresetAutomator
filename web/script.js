// create eel functions here
eel.expose(push_render_data);
function push_render_data(data) {
  Vue.prototype.$eel.app = data
}
eel.expose(log_data)
function log_data(info){
  Vue.prototype.$eel.log_data = info
}

Vue.prototype.$eel = new Vue({
  data:{
    app:null,
    log_data:null,
    show_application_data:false,
    arm_preset_storage:false
  },
  methods:{
    recall_camera_list: function(i){
      eel.recall_camera_list(i)
    },
    recall_camera:function(camera_number,i){
      eel.recall_camera(camera_number,i)
    },
    store_current_position:function(i){
      eel.store_current_position_as_preset(i)(x => window.alert(x))
    }
  },
  watch:{
  },
  computed:{
  }
})

Vue.component('camera-icon',{
  props:{camera:{type:Object}},
  computed: {
    style(){
      return{
        height:'200px',
        width:'200px',

      }
    },
    classList(){
      return{
        'bg-success': this.camera.connected && this.camera.preview && ! this.camera.program,
        'bg-danger':  this.camera.connected && this.camera.program,
        'bg-warning': ! this.camera.connected

      }
    }
  },
  template:`
    <div class="border rounded position-relative" :class="classList" :style="style">
        <span class="position-absolute top-50 start-50 translate-middle" v-html="camera.number"></span>
    </div>
  `
})

new Vue({
  el:document.getElementById('app')
})