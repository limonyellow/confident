import setuptools

setuptools.setup(
      name='confident',
      version='0.1.12',
      description='Loading configurations from multiple sources into a data model.',
      long_description=open('README.md').read(),
      long_description_content_type='text/markdown',
      url='https://github.com/limonyellow/confident',
      author='limonyellow',
      author_email='lemon@example.com',
      license='MIT',
      zip_safe=False,
      classifiers=[
            "Programming Language :: Python :: 3",
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3.8',
            'Programming Language :: Python :: 3.9',
            'Programming Language :: Python :: 3.10',
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
      ],
      packages=['confident'],
      install_requires=[
            'pydantic>=1.9.0',
            'pyyaml>=6.0',
            'python-dotenv>=0.10.4',
      ],
      python_requires=">=3.7",
)
