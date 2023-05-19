from PIL import Image
import os
import PIL


class Images:
    def __init__(self, path):
        self._path = path
        self.fixed_height = 350

    def resize_images(self):
        images_list = {file for file in os.listdir(self._path) if file.endswith(('jpeg', 'jpg', 'png', 'webp'))}
        number_images = len(images_list)
        if number_images == 0:
            print('\nNão há imagens na pasta "/{}"\n'.format(self._path))
        else:
            num = 0
            print('\nIniciando transformação das imagens!\nAguarde...\n')
            for image in images_list:
                img = Image.open('{}/{}'.format(self._path, image))
                height_percent = (self.fixed_height / float(img.size[1]))
                width_size = int((float(img.size[0]) * float(height_percent)))
                if (img.size[1] != 350) and (img.size[0] != width_size):
                    img = img.resize((width_size, self.fixed_height), PIL.Image.Resampling.NEAREST)
                    if '.png' in image:
                        self._convert_images(img, image)
                        os.remove('{}/{}'.format(self._path, image))
                    else:
                        img.save('{}/{}'.format(self._path, image), optmize=True, quality=100)
                    num += 1
            if num == 1:
                print('\n1 imagem teve o tamanho alterado!\n')
            elif num > 1:
                print('\n{} imagens tiveram o tamanho alterado!\n'.format(num))
            else:
                print('\nNenhuma imagem teve tamanho alterado!\n')
            print('\nFim das alterações das imagens!\n')

    def _convert_images(self, img, image):
        return img.save('{}/{}.webp'.format(self._path, image.split('.')[0]), 'webp', optmize=True, quality=40)

    def delete_all_images(self):
        import shutil

        folder = '{}'.format(self._path)
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('\nFalha ao deletar %s. Razão: %s\n' % (file_path, e))
