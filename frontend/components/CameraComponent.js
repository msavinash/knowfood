import React, { useState, useEffect } from "react";
import { Text, View, Button, Image } from "react-native";
import * as ImagePicker from "expo-image-picker";
import axios from "axios";
import * as FileSystem from "expo-file-system";

const BASE_URL = "http://192.168.1.77:5000";

const CameraComponent = () => {
  const [image, setImage] = useState(null);
  const [result, setResult] = useState("");

  useEffect(() => {
    (async () => {
      const { status } = await ImagePicker.requestCameraPermissionsAsync();
      if (status !== "granted") {
        alert("Permission to access camera is required!");
      }
    })();
  }, []);

  const takePicture = async () => {
    let result = await ImagePicker.launchCameraAsync({
      allowsEditing: false,
      aspect: [4, 3],
      quality: 1,
    });

    if (!result.cancelled) {
      const imageUri = result.assets[0].uri;
      //   console.log(result);
      //   console.log(result.assets[0].uri);
      //   console.log("PIC URI: " + result.uri);
      setImage(imageUri);
      sendPicture(imageUri);
    }
  };

  const sendPicture = async (uri) => {
    // setUploading(true);

    // setUploading(false);

    // check if uri is a file system path
    console.log("URI: " + uri.slice(0, 20));
    if (uri.startsWith("file://")) {
      console.log("Sending picture");

      await FileSystem.uploadAsync(BASE_URL + "/detect-text", uri, {
        httpMethod: "POST",
        uploadType: FileSystem.FileSystemUploadType.MULTIPART,
        fieldName: "file",
      })
        .then((response) => {
          console.log("SENT PICTURE");
          console.log("Response:");
          console.log(response);
          const text = JSON.parse(response.body).text;
          console.log(text);
          if (text.length > 0) {
            const ingredients = text[0];
            // send raw text to the server
            axios
              .post(BASE_URL + "/get-ingredients", ingredients)
              .then(function (response) {
                console.log("Ingredients Response:");
                console.log(response.data);
                setResult(JSON.stringify(response.data));
              });
          } else {
            setResult("No text detected");
          }
        })
        .catch((error) => {
          console.log("Error sending picture");
          console.error("Error sending picture:" + error);
          console.log(error.stack);
        });

      // Read the image file
      // const base64Img = await FileSystem.readAsStringAsync(uri, {
      //   encoding: FileSystem?.EncodingType?.Base64,
      // });

      //   console.log("​getFile -> base64Img", base64Img);

      //   let options = { encoding: FileSystem.EncodingTypes.Base64 };
      //   FileSystem.readAsStringAsync(uri, options)
      //     .then((data) => {
      //       const base64 = "data:image/jpg;base64" + data;
      //       resolve(base64); // are you sure you want to resolve the data and not the base64 string?
      //       console.log("​getFile -> data", data);
      //     })
      //     .catch((err) => {
      //       console.log("​getFile -> err", err);
      //       reject(err);
      //     });
      //   uri = "data:image/jpeg;base64," + base64Img;
      //   console.log("Sending picture");
      //   console.log(uri.slice(0, 10));
      //   const blob = await (await fetch(uri)).blob();
      //   console.log(blob);

      // let filename = uri.split("/").pop();

      // // Infer the type of the image
      // let match = /\.(\w+)$/.exec(filename);
      // let type = match ? `image/${match[1]}` : `image`;

      // Upload the image using the fetch and FormData APIs
      //   let formData = new FormData();
      //   // Assume "photo" is the name of the form field the server expects
      //   //   formData.append("file", { uri: uri, name: filename, type });
      //   formData.append("file", uri, "image.jpg");

      //   const formData = new FormData();
      //   formData.append(
      //     "file",
      //     JSON.stringify({
      //       uri: uri, // this is the path to your file. see Expo ImagePicker or React Native ImagePicker
      //       type: "image/jpg", // example: image/jpg
      //       name: `upload.jpg`, // example: upload.jpg
      //     })
      //   );

      // const newImageUri = uri;
      // const imguri = "data:image/jpg;base64" + base64Img;
      // const blob = await (await fetch(imguri)).blob();
      // const formData = new FormData();
      // formData.append("file", blob, "image.jpg");
      //   formData.append("image", {
      //     uri: newImageUri,
      //     // type: mime.getType(newImageUri),
      //     type: "image/jpeg",
      //     name: newImageUri.split("/").pop(),
      //   });

      // try {
      //   console.log("Sending request");
      //   console.log(formData);
      //   const response = await axios.post(
      //     "http://localhost:5000/detect-text",
      //     formData,
      //     {
      //       headers: {
      //         "Content-Type": "multipart/form-data",
      //       },
      //     }
      //   );
      //   const imageText = response.data.text[0];
      //   setResult(imageText);
      //   console.log("Response:");
      //   console.log(imageText);
      // } catch (error) {
      //   console.log("Error sending picture");
      //   console.error("Error sending picture:" + error);
      //   console.log(error.stack);
      // }
    } else {
      console.log("Sending picture");
      console.log(uri);
      const blob = await (await fetch(uri)).blob();
      console.log(blob);
      const formData = new FormData();
      formData.append("file", blob, "image.jpg");

      try {
        console.log("Sending request");
        console.log(formData);
        const response = await axios.post(
          "http://localhost:5000/detect-text",
          formData
        );
        const imageText = response.data.text[0];
        setResult(imageText);
        console.log("Response:");
        console.log(imageText);
      } catch (error) {
        console.log("Error sending picture");
        console.error("Error sending picture:" + error);
      }
    }
  };

  return (
    <View style={{ flex: 1, alignItems: "center", justifyContent: "center" }}>
      <Button title="Take Picture" onPress={takePicture} />
      {image && (
        <Image source={{ uri: image }} style={{ width: 200, height: 200 }} />
      )}
      {result ? <Text>{result}</Text> : null}
    </View>
  );
};

export default CameraComponent;
