document.addEventListener("DOMContentLoaded", () => {
//  ----- >>>>>>>>    starting the Edit functionality
    document.querySelectorAll(".edit-button").forEach(button => {
        button.addEventListener("click", function() {
           const idPost = button.dataset.postId;
        //    console.log(idPost);
           const post = document.getElementById(`post-${idPost}`);
        //    const post = document.getElementById("post-"+idPost);
           const content = post.querySelector(".post-content");
           content.classList.add("d-none");

           const likeUnlike = post.querySelector(".like-button");
           likeUnlike.classList.add("d-none");

           const contentEdit = post.querySelector(".post-edit");
           contentEdit.classList.remove("d-none");
           button.classList.add("d-none");

           const contenCurrent = content.querySelector(".card-text").textContent;
           console.log(contenCurrent);
           const newContent = contentEdit.querySelector(".edit-text");
           newContent.value = contenCurrent;

           const saveButton = post.querySelector(".save-text");

           saveButton.addEventListener("click", function(){
            fetch(`/edit-post/${idPost}`, {
                        method: "PUT",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ content: newContent.value })
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.error) {
                            alert(data.error);
                            return;
                        }
                        const contentUpDated = data.content;
                        const elementContent = content.querySelector(".card-text");
                        elementContent.textContent = contentUpDated;
                        content.classList.remove("d-none");
                        contentEdit.classList.add("d-none");
                        likeUnlike.classList.remove("d-none");
                        button.classList.remove("d-none");

                        });
           })
        });
    });
//  ----- >>>>>>>>     ending the Edit functionality

//  ----- >>>>>>>>    starting the Like and Unlike functionality
    document.querySelectorAll(".like-button").forEach(button => {
        button.addEventListener("click", function() {
            const likePost = button.dataset.postLike;
            const post = document.getElementById("post-"+likePost);
            const btnLike = post.querySelector(".like-button");
            const btnLikeValue = btnLike.textContent;
            const likesCount = post.querySelector(".likes-count");

            fetch(`/like/${likePost}`)
            .then(res => res.json())
            .then(data => {
                if (data.error) {
                    alert(data.error);
                    return;
                }
                // console.log(data.like_count);
                if(btnLikeValue == "Like"){
                    btnLike.textContent = "Unlike";
                }else{
                    btnLike.textContent = "Like";
                }
                likesCount.textContent = data.like_count;
                });

        });
    });
//  ----- >>>>>>>>     ending the Like and Unlike functionality
});
