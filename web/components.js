Vue.component('td-camera-position',{
    props:{
        cameraIndex:{type:Number,required:true},
        presetIndex:{type:Number,required:true}
    },
    computed:{
        position:function (){
            return this.$eel.capturedPositions[this.cameraIndex][this.presetIndex]
        }
    },
    template:`<td v-html="position"></td>`

});
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
          'bg-warning': ! this.camera.connected,
          'border-primary border-5': this.camera.is_moving
      }
    }
  },
  template:`
    <div class="border rounded position-relative" :class="classList" :style="style">
        <span v-if="camera.needs_restart">PLEASE RESTART CAMERA<br/>then launch app again</span>
        <span v-else class="position-absolute top-50 start-50 translate-middle" v-html="camera.number"></span>
    </div>
  `
});
Vue.component('group-presets',{
    template:`
        <div>
            <div v-for="row in [1,2,3,4]" class="mb-3 d-flex justify-content-between" style="max-width: 600px">
                <preset-button
                    v-for="col in [1,2,3,4]"
                    :key="(row - 1) * 4 + col"
                    :number="(row - 1) * 4 + col"
                    :btn-version="btnVersion"
                ></preset-button>
            </div>
        </div>
    `,
    computed:{
        btnVersion: function(){
                    if(this.$eel.arm_preset_storage){
                        return 'btn-danger'
                    }else if(this.$eel.arm_capture){
                        return 'btn-success'
                    }else{
                        return 'btn-primary'
                    }
        }
    },
    components:{
        "preset-button":{
            props:{
                number:{required:true,type:Number},
                btnVersion:{required:true,type:String}
            },
            data:function(){
                return{
                    storing:false,
                }
            },
            methods:{
                handle_click:function(){
                    if(this.$eel.arm_preset_storage) {
                        this.storing = true
                        this.$eel.store_current_position_as_preset(this.number,(x) => {
                            this.storing = false
                            window.alert(x)
                        })
                    }else if (this.$eel.arm_capture){
                        this.$eel.capture(this.number - 1)
                    }else{
                        this.$eel.recall_camera_list(this.number)
                    }
                }
            },
            computed:{
                name:function(){
                    return 'Preset '+this.number
                },
                disabled:function(){
                    if(this.storing || this.$eel.recalling ){
                        return true;
                    }
                },
            },
            template:`
            <button
                    class="btn "
                    :class="btnVersion"
                    style="width:100px;"
                    :disabled="disabled"
                    @click="handle_click()"
                    v-html="name"
            ></button>
            `
        }
    }
});
Vue.component('capture-data',{
    props:{
        height:{type:Number, required:true}
    },
    data:function(){
        return {
            filename:'Camera Preset Automator - Preset Dump',
        }
    },
    methods:{
        exportPresets:function(){
            var blob = new Blob([JSON.stringify(this.$eel.capturedPositions)], {type: "application/json;charset=utf-8"});
            saveAs(blob,this.filename + '.json')
        }
    },
    template:`
<div>
    <div class="input-group mb-3">
        <input type="text" class="form-control" v-model="filename">
        <div class="input-group-append">
            <button class="btn btn-primary" type="button"
                @click="exportPresets()" 
            >Export Presets</button>
        </div>
    </div>
    <div :style="{height:height - 35+ 'px'}" style="overflow-y: scroll;font-size:.7em;">
        <table class="table table-sm" :class="{'table-dark':$eel.darkMode}" >
            <thead>
                <tr><th>#</th><th>Cam1</th><th>Cam2</th><th>Cam3</th><th>Cam4</th><th>Cam5</th></tr>   
            </thead>    
            <tbody>
                <tr v-for="ci in [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]" :key="ci">
                    <td v-html="ci + 1"></td>
                    <td
                        v-for="ri in [0,1,2,3,4]"
                        :key="ci + '-' + ri"
                        is="td-camera-position"
                        :camera-index="ri"
                        :preset-index="ci"
                    ></td>
                </tr>
            </tbody>
        </table>
    </div>

    
</div>
    `
});

Vue.component('import-presets',{
    data:function(){
        return {
            imported:null,
            uploaded:null,
            uploaded_filename:null,
        }
    },
    methods:{
        handleFileInput:function(e){
            var file = e.target.files[0]
            var reader = new FileReader()
            reader.onloadend= (f ) => {
                try{
                    this.uploaded = JSON.parse(reader.result)
                    this.uploaded_filename = file.name
                }catch (e){
                    window.alert(e.message)
                }
            }
            reader.readAsText(file)
        },
        load_preset_list:function(){
            eel.load_preset_list(this.uploaded)( ok => {
                    window.alert(ok)
                    this.imported =  true
                    this.$eel.loading_presets = false;
            })
        }
    },
    template:`
<div>
    <p>You can upload a presets.json file below. Once it's imported successfully, the presets are stored to the camera system.</p>
    <p v-if="imported">
        <strong>Imported: </strong><span v-html="uploaded_filename"></span>
    </p>
    <div class="input-group my-3">
        <div class="custom-file">
            <input type="file" class="form-control" @change="handleFileInput($event)" >
        </div>
        <div class="input-group-append">
            <button class="btn btn-primary" @click="load_preset_list()" :disabled="uploaded === null">
                <span v-if="uploaded === null">1: Add a preset file</span>
                <span v-else>2: Click here to Import</span>
            </button>
        </div>
    </div>
</div>
    `
})