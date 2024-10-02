<template>
  <div id="app">
    <h1>Image Upload</h1>
    <input type="file" @change="onFileChange" />
    <button @click="uploadFile">Upload</button>

    <div v-if="imageInfo">
      <h3>Uploaded Image Information:</h3>
      <p>Filename: {{ imageInfo.filename }}</p>
      <p>Size: {{ imageInfo.size }} bytes</p>

      <!-- 미리보기 이미지 표시 -->
      <img
        :src="imageUrl"
        alt="Uploaded Image"
        v-if="imageUrl"
        style="margin-top: 20px; max-width: 100%; height: auto;"
      />
      
      <!-- 렌더링할 HTML 내용 -->
      <div v-html="imageInfo.inference_result" style="margin-top: 20px;"></div>
    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  data() {
    return {
      selectedFile: null,
      imageInfo: null, // 백엔드로부터 받은 이미지 정보를 저장
      imageUrl: null, // 업로드한 이미지 URL
    };
  },
  methods: {
    // 파일 선택 시 처리
    onFileChange(event) {
      this.selectedFile = event.target.files[0];
      
      // 선택한 파일의 URL을 생성하여 미리보기로 설정
      if (this.selectedFile) {
        this.imageUrl = URL.createObjectURL(this.selectedFile);
      }
    },
    // 파일 업로드
    async uploadFile() {
      if (!this.selectedFile) {
        alert("Please select a file first!");
        return;
      }

      const formData = new FormData();
      formData.append("file", this.selectedFile);

      try {
        // Axios를 통해 서버에 파일 업로드 요청
        const response = await axios.post("http://localhost:8000/upload/", formData, {
          headers: {
            "Content-Type": "multipart/form-data",
          },
          timeout: 600000, // 10분 타임아웃 설정 (600000ms)
        });

        // 응답 데이터를 imageInfo에 저장
        this.imageInfo = response.data;
      } catch (error) {
        console.error("Error uploading file:", error);
        if (error.code === 'ECONNABORTED') {
          alert("Upload timed out after 10 minutes. Please try again.");
        } else {
          alert("Error uploading file");
        }
      }
    },
  },
};
</script>

<style scoped>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  text-align: center;
  margin-top: 60px;
}
input {
  margin-bottom: 20px;
}
</style>
